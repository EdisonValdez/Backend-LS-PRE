#!/bin/bash
# author: dzamora, apoquet
# version: 1.0
# '######################################################'
# '#         DigitalOcean Django cloud deploy utility         #'
# '######################################################'

trap 'exit 1' INT # This allows to cancel whole script, not order by order
basename=$(basename "$0")
dump_filename='dump.pgsql'
var_regex="s/.*=(.*)/\1/g"

usage="
Usage: $basename ACTION <environment> [OPTIONS]

A management utility to manage deployment into DigitalOcean Droplet

Actions:
  help              Prints this help message
  deploy            Performs a deploy into specified environment
  migrate           Performs a django migrate command into specified environment
  collect           Performs a django collectstatic command into specified environment
  createsuperuser   Performs a custom django command to create a superuser into specified environment
  seed              Performs a custom django command to seed the database with fake models into specified environment
  bash              Starts a shell session with the specified environment
  shell_plus        Performs a django shell_plus command into specified environment
  backup_db         Performs a database backup from specified environment
  restore_db        Performs a database restore into specified environment

Environments:
    A list of available environments inside .docker/*.yml

Options:
  --help            Prints this help message

Run '$basename help' for print this information.
"

main_func()
{
    action="$1"
    if [[ "$action" == 'help' ]]; then
        echo "$usage"
    elif [[ "$action" == 'deploy' ]]; then
        echo 'Launching deploy action:'
        if [[ "$(is_in_project)" -gt 0 ]]; then
            compose_file=$(get_compose_file "$2")
            if [[ -f "$compose_file" ]] && [[ "$3" == '--soft' ]]; then
                deploy_only_code "$compose_file"
            elif [[ -f "$compose_file" ]]; then
                deploy "$compose_file"
            else
                echo -n 'The given environment has not been found. Available options: '
                load_options
            fi
        else
            echo 'You must run this command into root of rudo-based project to work' >&2
        fi
    elif [[ "$action" == 'migrate' ]]; then
        echo 'Launching migrate action:'
        if [[ "$(is_in_project)" -gt 0 ]]; then
            compose_file=$(get_compose_file "$2")
            if [[ -f "$compose_file" ]]; then
                migrate "$compose_file"
            else
                echo -n 'The given environment has not been found. Available options: '
                load_options
            fi
        else
            echo 'You must run this command into root of rudo-based project to work' >&2
        fi
    elif [[ "$action" == 'collect' ]]; then
        echo 'Launching collect action:'
        if [[ "$(is_in_project)" -gt 0 ]]; then
            compose_file=$(get_compose_file "$2")
            if [[ -f "$compose_file" ]]; then
                collect "$compose_file"
            else
                echo -n 'The given environment has not been found. Available options: '
                load_options
            fi
        else
            echo 'You must run this command into root of rudo-based project to work' >&2
        fi
    elif [[ "$action" == 'createsuperuser' ]]; then
        echo 'Launching collect action:'
        if [[ "$(is_in_project)" -gt 0 ]]; then
            compose_file=$(get_compose_file "$2")
            if [[ -f "$compose_file" ]]; then
                superuser "$compose_file"
            else
                echo -n 'The given environment has not been found. Available options: '
                load_options
            fi
        else
            echo 'You must run this command into root of rudo-based project to work' >&2
        fi
    elif [[ "$action" == 'seed' ]]; then
        echo 'Launching collect action:'
        if [[ "$(is_in_project)" -gt 0 ]]; then
            compose_file=$(get_compose_file "$2")
            if [[ -f "$compose_file" ]]; then
                seed "$compose_file" "$3"
            else
                echo -n 'The given environment has not been found. Available options: '
                load_options
            fi
        else
            echo 'You must run this command into root of rudo-based project to work' >&2
        fi
    elif [[ "$action" == 'bash' ]]; then
        echo 'Launching bash session:'
        if [[ "$(is_in_project)" -gt 0 ]]; then
            compose_file=$(get_compose_file "$2")
            if [[ -f "$compose_file" ]]; then
                bash "$compose_file"
            else
                echo -n 'The given environment has not been found. Available options: '
                load_options
            fi
        else
            echo 'You must run this command into root of rudo-based project to work' >&2
        fi
    elif [[ "$action" == 'shell_plus' ]]; then
        echo 'Launching shell_plus command:'
        if [[ "$(is_in_project)" -gt 0 ]]; then
            compose_file=$(get_compose_file "$2")
            if [[ -f "$compose_file" ]]; then
                shell_plus "$compose_file"
            else
                echo -n 'The given environment has not been found. Available options: '
                load_options
            fi
        else
            echo 'You must run this command into root of rudo-based project to work' >&2
        fi
    elif [[ "$action" == 'backup_db' ]]; then
        echo 'Launching backup_db action:'
        if [[ "$(is_in_project)" -gt 0 ]]; then
            compose_file=$(get_compose_file "$2")
            if [[ -f "$compose_file" ]]; then
                backup_db "$compose_file"
            else
                echo -n 'The given environment has not been found. Available options: '
                load_options
            fi
        else
            echo 'You must run this command into root of rudo-based project to work' >&2
        fi
    elif [[ "$action" == 'restore_db' ]]; then
        echo 'Launching restore_db action:'
        if [[ "$(is_in_project)" -gt 0 ]]; then
            compose_file=$(get_compose_file "$2")
            if [[ -f "$compose_file" ]]; then
                restore_db "$compose_file"
            else
                echo -n 'The given environment has not been found. Available options: '
                load_options
            fi
        else
            echo 'You must run this command into root of rudo-based project to work' >&2
        fi
    else
        echo "$usage"
    fi
}

is_in_project()
{
    count=$(find .docker -maxdepth 1 -name '*.yml' 2>/dev/null |wc -l |xargs)
    ret=0
    if [[ "$count" -gt 0 ]]; then
        ret=1
    else
        ret=0
    fi
    echo "$ret"
}

get_compose_file()
{
    echo ".docker/$1.yml"
}

load_options()
{
    options=""
    dirs=$(find .docker -maxdepth 1 -name '*.yml' 2>/dev/null)
    for entry in $dirs;
    do
        options+="$(basename "$entry" .yml) "
    done
    echo "$options"
}

security_question()
{
    if [[ -z "$DOCKER_MACHINE_NAME" ]]; then
        echo >&2 'You are not using any docker-machine environment'
        echo >&2 'You are sure that you want to deploy anyway?'
        echo >&2 '(default behavior installs it into your local docker installation)'
    else
        echo >&2 "You are pointing to <$DOCKER_MACHINE_NAME> environment"
        echo >&2 'You are sure that you want to deploy anyway?'
    fi
    echo -n >&2 '(y/N): '
    read -r continue_action
    echo "$continue_action"
}

deploy()
{
    rsp=$(if [[ "$2" == '--y' ]]; then echo 'y'; else security_question; fi)
    if [[ "$rsp" == 'y' ]]; then
        echo 'Performing deployment:'
        docker-compose -f "$1" build
        docker-compose -f "$1" stop
        docker-compose -f "$1" rm -f
        docker-compose -f "$1" up -d --remove-orphans
        docker system prune --force
        migrate "$1" "$rsp"
        collect "$1"
    else
        echo 'Deployment action aborted'
    fi
}

deploy_only_code()
{
    rsp=$(if [[ "$2" == '--y' ]]; then echo 'y'; else security_question; fi)
    if [[ "$rsp" == 'y' ]]; then
        echo 'Performing soft deployment:'
        docker exec -t web rm -rf /code/*
        docker cp . web:/code
        migrate "$1" "$rsp"
        collect "$1"
    else
        echo 'Deployment action aborted'
    fi
}

migrate()
{
    rsp="$2" || security_question ''
    if [[ "$rsp" == 'y' ]]; then
        echo 'Performing migrate:'
        docker-compose -f "$1" exec web python manage.py migrate
    else
        echo 'Deployment action aborted'
    fi
}

collect()
{
    echo 'Performing collectstatic:'
    docker-compose -f "$1" exec web python manage.py collectstatic --noinput
}

superuser()
{
    echo 'Performing supersu creation:'
    docker-compose -f "$1" exec web python manage.py create_superuser
}

seed()
{
    echo 'Performing seeding:'
    if [[ -n $2 ]]; then
        docker-compose -f "$1" exec web python manage.py seed_database "$2"
    else
        docker-compose -f "$1" exec web python manage.py seed_database
    fi

}

bash()
{
    echo 'Performing bash session:'
    docker-compose -f "$1" exec web bash
}

shell_plus()
{
    echo 'Performing shell_plus:'
    docker-compose -f "$1" exec web python manage.py shell_plus
}

backup_db()
{
    echo 'Performing db backup:'
    # This action is made to be used only in dev env as no postgres container may be used in production env.
    env=$(cat "$1")
    env_file=$(echo "$env" |grep 'env_file: ' |head -1 |sed -E -e "s/env_file: (.*)/.docker\/\1/g" |xargs)
    pg_usr=$(grep 'POSTGRES_USER' <"$env_file" |sed -E -e "$var_regex" |xargs)
    pg_pwd=$(grep 'POSTGRES_PASSWORD' <"$env_file" |sed -E -e "$var_regex" |xargs)
    pg_dbn=$(grep 'POSTGRES_DB' <"$env_file" |sed -E -e "$var_regex" |xargs)
    pg_hst=$(grep 'POSTGRES_HOST' <"$env_file" |sed -E -e "$var_regex" |xargs)

    docker-compose -f "$1" exec -T -e "PGPASSWORD=$pg_pwd" "$pg_hst" pg_dump -c -U "$pg_usr" -Fc "$pg_dbn" >$dump_filename
}

restore_db()
{
    echo 'Performing db backup restore:'
    # This action is made to be used only in dev env as no postgres container may be used in production env.
    env=$(cat "$1")
    env_file=$(echo "$env" |grep 'env_file: ' |head -1 |sed -E -e "s/env_file: (.*)/.docker\/\1/g" |xargs)
    pg_usr=$(grep 'POSTGRES_USER' <"$env_file" |sed -E -e "$var_regex" |xargs)
    pg_pwd=$(grep 'POSTGRES_PASSWORD' <"$env_file" |sed -E -e "$var_regex" |xargs)
    pg_dbn=$(grep 'POSTGRES_DB' <"$env_file" |sed -E -e "$var_regex" |xargs)
    pg_hst=$(grep 'POSTGRES_HOST' <"$env_file" |sed -E -e "$var_regex" |xargs)

    docker-compose -f "$1" exec -T -e "PGPASSWORD=$pg_pwd" "$pg_hst" pg_restore -U "$pg_usr" -c -Fc -d "$pg_dbn" <"$dump_filename"
}

main_func "$@"
