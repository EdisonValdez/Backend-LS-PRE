#!/bin/bash
# author: dzamora, apoquet
# version: 1.0
# '######################################################'
# '#      Docker Machine remote management utility      #'
# '######################################################'
## --- Symlink creation ---
##     ln -s ~/scripts/docker_cloud.sh /usr/local/bin/docker-cloud
## --- Symlink creation ---
##
## --- Environment variables configuration ---
##     # Add the following lines to the end of your shell rc file (~/.zshrc):
##     # Dashboard machines cloud sync token
##     export TEAMCERTS_ACCESS_TOKEN=zc54f...
##     # Digital Ocean
##     export DO_ACCESS_TOKEN=ea9dd...
##     # AWS
##     export AWS_ACCESS_KEY_ID=AKIAV...
##     export AWS_SECRET_ACCESS_KEY=lp6Bp...
## --- Environment variables configuration ---

region=fra1
image=ubuntu-20-04-x64
ec2_region=eu-west-1
ec2_instance_type=t3.micro
basename=$(basename "$0")
certs_file='certs-team.tar.gz'
certs_url="https://dashboard.rudo.es/dashboard/$certs_file"
certs_auth="X-Api-Access-Token: $TEAMCERTS_ACCESS_TOKEN"
upgrade_machine=1

usage="
Usage: $basename ACTION [OPTIONS]

A management utility to interact with Cloud Computing providers, i.e DigitalOcean and AWS

Actions:
  help              Prints this help message
  list              Prints Docker Machine environments
  containers        Prints a list of Docker containers (additional machine_options could be passed)
  free              Unlinks environment variables to use local Docker (must be used with preceding '.' ex: ~ % . $basename free)
  create            Creates a Docker Droplet into DigitalOcean account (requires environment name and DO_ACCESS_TOKEN environment variable) (--aws option can be used to generate it into AWS, requires AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables)
  provision         Re-provision existing machines (requires environment name)
  shellm            Starts an interactive shell with a given environment (requires environment name)
  shellc            Starts an interactive shell with a given container (requires container name)
  remove            Deletes a Docker Machine within your local installation (requires environment name)
  start             Starts an existing Docker Machine from your local installation (requires environment name)
  stop              Stops an existing Docker Machine from your local installation (requires environment name)
  restart           Restarts an existing Docker Machine from your local installation (requires environment name)
  use               Makes a link with docker environment to be used from local (an environment name could be given) (must be used with preceding '.' ex: ~ % . $basename use machine_name)
  certs             Installs the team certificate to share authentication between team members (requires environment name and TEAMCERTS_ACCESS_TOKEN environment variable) (--renew || --renew-ca || --aws options can be passed) (child actions can be directly passed)
  deploy            Starts a deployment process into the current activated docker machine environment (requires environment target) (soft deployment can be made, aka only-code-deploy)
  migrate           Starts a migrate process into the current activated docker machine environment
  vars              Prints environment configuration of DOCKER_* variables
  cloud             Launched the cloud sync script to perform a supported action (child actions can be directly passed, requires TEAMCERTS_ACCESS_TOKEN environment variable)

Options:
  -a                Lists all available elements (only works with <ps> action)

Run '$basename help' for print this information.
"

main_func()
{
    action="$1"
    if [[ "$action" == 'help' ]]; then
        echo "$usage"
    elif [[ "$action" == 'list' ]] || [[ "$action" == 'ls' ]]; then
        echo 'List of Docker Machines:'
        docker-machine ls
    elif [[ "$action" == 'containers' ]] || [[ "$action" == 'ps' ]]; then
        echo 'List of Docker Containers:'
        eval "docker ps $2"
    elif [[ "$action" == 'free' ]]; then
        if [[ "$0" == "${BASH_SOURCE[0]}" ]]; then
            echo "This command must be run with preceding dot (~ % . $basename $1) to take effect"
        else
            echo 'Unlink Docker Machine environment'
            unset DOCKER_TLS_VERIFY
            unset DOCKER_HOST
            unset DOCKER_CERT_PATH
            unset DOCKER_MACHINE_NAME
        fi
    elif [[ "$action" == 'create' ]]; then
        echo 'Docker Machine creation:'
        if [[ "$#" -gt 1 ]] && [[ -n "$2" ]]; then
            if [[ "$3" == '--aws' ]]; then
                if [[ -n "$AWS_ACCESS_KEY_ID" ]] && [[ -n "$AWS_SECRET_ACCESS_KEY" ]]; then
                    if [[ -x $(command -v aws) ]]; then
                        machine_path="$HOME/.docker/machine/machines/$2"
                        vpcid=$(aws ec2 describe-vpcs --filters Name=is-default,Values=true |grep VpcId |sed -E -e 's/"VpcId": "(.*)",/\1/g' |xargs)
                        eval "docker-machine create --driver amazonec2 --amazonec2-vpc-id $vpcid --amazonec2-region $ec2_region --amazonec2-instance-type $ec2_instance_type $2"
                        rule_80_created=$(aws ec2 describe-security-groups --group-names docker-machine --filters Name=ip-permission.cidr,Values=0.0.0.0/0 --filters Name=ip-permission.from-port,Values=80 |wc -l |xargs)
                        rule_443_created=$(aws ec2 describe-security-groups --group-names docker-machine --filters Name=ip-permission.cidr,Values=0.0.0.0/0 --filters Name=ip-permission.from-port,Values=443 |wc -l |xargs)
                        if [[ "$rule_80_created" -le 3 ]]; then
                            aws ec2 authorize-security-group-ingress --group-name docker-machine --protocol tcp --port 80 --cidr 0.0.0.0/0
                        fi
                        if [[ "$rule_443_created" -le 3 ]]; then
                            aws ec2 authorize-security-group-ingress --group-name docker-machine --protocol tcp --port 443 --cidr 0.0.0.0/0
                        fi
                        echo 'Configuring into machine config.json'
                        sed -E -i '' -e '/(\/machines\/)+/! s/"(.*)\.docker\/machine\/[a-zA-Z0-9_-]+(.*)"/"\1.docker\/machine\/certs-team\2"/g' "$machine_path/config.json"
                        # With this command we enable root access to the machine
                        docker-machine ssh "$2" sudo cp /root/.ssh/authorized_keys /root/.ssh/authorized_keys.bkp
                        docker-machine ssh "$2" "sudo sed -E -i -e 's/.*(ssh-rsa.*)/\1/' /root/.ssh/authorized_keys"
                        if [[ 0 -gt 1 ]] && [[ $upgrade_machine -gt 0 ]]; then
                            # Temporarily disabled due to grub update
                            echo 'Upgrading remote machine packages'
                            docker-machine ssh "$2" "sudo apt-get update && sudo apt-get upgrade -y && sudo reboot"
                            echo 'Waiting EC2 instance 60s to be rebooted'
                            sleep 60
                        fi
                        main_func provision "$2"
                        main_func certs "$2" --renew --aws
                    else
                        echo 'AWS CLI is required to perform Docker configuration into AWS'
                        echo 'You can install it by running: pip3 install awscli'
                    fi
                else
                    echo 'AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables are needed to interact with AWS'
                fi
            elif [[ -n "$DO_ACCESS_TOKEN" ]]; then
                machine_path="$HOME/.docker/machine/machines/$2"
                eval "docker-machine create --driver digitalocean --digitalocean-access-token=$DO_ACCESS_TOKEN --digitalocean-region=$region --digitalocean-image=$image $2"
                docker-machine ssh "$2" "service docker restart"
                echo 'Configuring into machine config.json'
                sed -E -i '' -e '/(\/machines\/)+/! s/"(.*)\.docker\/machine\/[a-zA-Z0-9_-]+(.*)"/"\1.docker\/machine\/certs-team\2"/g' "$machine_path/config.json"
                if [[ $upgrade_machine -gt 0 ]]; then
                    echo 'Upgrading remote machine packages'
                    docker-machine ssh "$2" "apt-get update && apt-get upgrade -y && reboot"
                    echo 'Waiting droplet 30s to be rebooted'
                    sleep 30
                fi
                main_func provision "$2"
                main_func certs "$2" --renew
            else
                echo 'DO_ACCESS_TOKEN environment variable is needed to interact with DigitalOcean'
            fi
        else
            echo 'A machine name param after action is needed to use this action'
        fi
    elif [[ "$action" == 'provision' ]]; then
        echo 'Docker Machine re-provision:'
        if [[ "$#" -gt 1 ]] && [[ -n "$2" ]]; then
            machine_path="$HOME/.docker/machine/machines/$2"
            if [[ -f "$machine_path/key.pem" ]]; then
                chmod 600 "$machine_path/key.pem"
            fi
            eval "docker-machine provision $2"
        else
            echo 'A machine name param after action is needed to use this action'
        fi
    elif [[ "$action" == 'shellm' ]]; then
        echo 'Docker Machine connect:'
        if [[ "$#" -gt 1 ]] && [[ -n "$2" ]]; then
            eval "docker-machine ssh $2"
        else
            echo 'A machine name param after action is needed to use this action'
        fi
    elif [[ "$action" == 'shellc' ]]; then
        echo 'Docker container connect:'
        if [[ "$#" -gt 1 ]] && [[ -n "$2" ]]; then
            eval "docker exec -it $2 bash"
        else
            echo 'A container name param after action is needed to use this action'
        fi
    elif [[ "$action" == 'remove' ]] || [[ "$action" == 'rm' ]]; then
        echo 'Docker Machine remove:'
        if [[ "$#" -gt 1 ]] && [[ -n "$2" ]]; then
            eval "docker-machine rm $2"
        else
            echo 'A machine name param after action is needed to use this action'
        fi
    elif [[ "$action" == 'start' ]]; then
        echo 'Docker Machine start:'
        if [[ "$#" -gt 1 ]] && [[ -n "$2" ]]; then
            eval "docker-machine start $2"
        else
            echo 'A machine name param after action is needed to use this action'
        fi
    elif [[ "$action" == 'stop' ]]; then
        echo 'Docker Machine stop:'
        if [[ "$#" -gt 1 ]] && [[ -n "$2" ]]; then
            eval "docker-machine stop $2"
        else
            echo 'A machine name param after action is needed to use this action'
        fi
    elif [[ "$action" == 'restart' ]]; then
        echo 'Docker Machine restart:'
        if [[ "$#" -gt 1 ]] && [[ -n "$2" ]]; then
            eval "docker-machine restart $2"
        else
            echo 'A machine name param after action is needed to use this action'
        fi
    elif [[ "$action" == 'use' ]]; then
        echo 'Docker Machine environment link:'
        if [[ "$0" == "${BASH_SOURCE[0]}" ]]; then
            echo "This command must be run with preceding dot (~ % . $basename $1) to take effect"
        else
            if [[ "$#" -gt 1 ]] && [[ -n "$2" ]]; then
                echo "Linking to [$2]"
                eval "$(docker-machine env "$2")"
            else
                machines_path=~/.docker/machine/machines
                if [[ -d "$machines_path" ]]; then
                    machine_options=("Cancel")
                    # shellcheck disable=SC2044
                    for entry in $(find "$machines_path" -maxdepth 1 -mindepth 1 -type d 2>/dev/null);
                    do
                        machine_options+=("$(basename "$entry")")
                    done
                    select opt in "${machine_options[@]}"
                    do
                        case $opt in
                            "Cancel")
                                echo 'Doing nothing'
                                ;;
                            *)
                                if [[ " ${machine_options[*]} " =~ ${opt} ]]; then
                                    eval "$(docker-machine env "$opt")"
                                    echo "Linked to [$opt]"
                                else
                                    echo 'Chosen option out of range'
                                fi
                                ;;
                        esac
                        break;
                    done
                    unset machine_options
                else
                    echo 'There are no docker machines configured to use'
                fi
            fi
        fi
    elif [[ "$action" == 'certs' ]]; then
        echo 'Docker Machine team certificates configuration:'
        docker_machine_certs_path="$HOME/.docker/machine"
        team_certs_path="$docker_machine_certs_path/certs-team"

        if [[ ! -d "$team_certs_path" ]]; then
            echo "Downloading team certificates"
            cur_dir=$(pwd)
            cd "$docker_machine_certs_path" || exit
            curl -O "$certs_url" --header "$certs_auth"
            tar -xvzf "$certs_file"
            rm "$certs_file"
            cd "$cur_dir" || exit
            echo "Team certificates installed into $team_certs_path"
        fi

        if [[ "$#" -gt 1 ]] && [[ -n "$2" ]]; then
            machine_path="$docker_machine_certs_path/machines/$2"
            if [[ -d "$machine_path" ]]; then
                echo "Checking Docker Machine team certificate configuration into given machine <$2>:"
                regex=("\"CertDir\": \".*certs-team.*\"" \
                    "\"CaCertPath\": \".*certs-team.*\"" \
                    "\"CaPrivateKeyPath\": \".*certs-team.*\"" \
                    "\"ClientKeyPath\": \".*certs-team.*\"" \
                    "\"ClientCertPath\": \".*certs-team.*\"")
                matches=0
                for str in "${regex[@]}"; do
                    matches=$(grep -Ei "$str" "$machine_path/config.json" |wc -c | xargs)
                    if [[ "$matches" -eq 0 ]]; then break; fi
                done

                if [[ "$matches" -eq 0 ]]; then
                    if [[ "$3" == '--y' ]]; then
                        set_certs='y'
                    else
                        echo "The given environment <$2> does not have the team certificates set. Do you want to set it?"
                        echo -n '(y/N): '
                        read -r set_certs
                    fi

                    if [[ "$set_certs" == 'y' ]]; then
                        echo 'Configuring into machine config.json'
                        # This changes the certs path to team certs path
                        sed -E -i '' -e '/(\/machines\/)+/! s/"(.*)\.docker\/machine\/[a-zA-Z0-9_.-]+(.*)"/"\1.docker\/machine\/certs-team\2"/g' "$machine_path/config.json"
                        # This changes the machine home dir to your current home dir
                        sed -E -i '' -e 's#"/Users/(.*)/(.docker/)(.*)"#"'"$HOME/"'\2\3"#g' "$machine_path/config.json"
                    else
                        echo 'The certificates have not been configured'
                        exit
                    fi
                else
                    echo "The team certificates for given docker machine <$2> is currently well configured"
                fi

                if [[ "$#" -gt 2 ]] && [[ -n "$3" ]] && { [[ "$3" == '--renew-ca' ]] || [[ "$4" == '--renew-ca' ]]; } then
                    echo "Docker Machine renewal of ca certificates on team certificates into machine $2:"
                    util_dir="$team_certs_path/c_gen"
                    bash "$util_dir/gen_team_certs.sh"
                fi

                if [[ "$#" -gt 2 ]] && [[ -n "$3" ]] && { [[ "$3" == '--renew' ]] || [[ "$4" == '--renew' ]]; } then
                    echo "Docker Machine renewal of server certificate based on team certificates into machine $2:"
                    days_validity=36525
                    key_length=2048
                    csr_path="$team_certs_path/c_gen/server.csr"
                    config_file="$team_certs_path/c_gen/tls-req.conf"
                    openssl genrsa -out "$machine_path/server-key.pem" $key_length
                    machine_ip=$(docker-machine url "$2" |sed -E -e "s/tcp:\/\/(.*):.*/\1/g")
                    sed -E -i '' -e "s/(subjectAltName)(.*)IP:(.*)/\1\2IP:$machine_ip/g" "$config_file"
                    openssl req -new -key "$machine_path/server-key.pem" -config "$config_file" -subj "/O=RUDO/C=ES" -out "$csr_path"
                    openssl x509 -req -sha256 -in "$csr_path" -CA "$team_certs_path/ca.pem" -CAkey "$team_certs_path/ca-key.pem" -CAcreateserial -out "$machine_path/server.pem" -days $days_validity -extfile "$config_file" -extensions server_crt
                    rm -f "$team_certs_path/c_gen/server.csr"
                    if [[ "$4" == '--aws' ]] || [[ "$5" == '--aws' ]]; then
                        docker-machine scp "$machine_path/server-key.pem" "root@$2:/etc/docker/server-key.pem"
                        docker-machine scp "$machine_path/server.pem" "root@$2:/etc/docker/server.pem"
                        docker-machine scp "$team_certs_path/ca.pem" "root@$2:/etc/docker/ca.pem"
                        docker-machine ssh "$2" sudo service docker restart
                        if [[ -n "$(docker-machine ssh "$2" sudo docker ps -aq)" ]]; then
                            docker-machine ssh "$2" "sudo docker start \$(sudo docker ps -aq)"
                        fi
                    else
                        docker-machine scp "$machine_path/server-key.pem" "$2:/etc/docker/server-key.pem"
                        docker-machine scp "$machine_path/server.pem" "$2:/etc/docker/server.pem"
                        docker-machine scp "$team_certs_path/ca.pem" "$2:/etc/docker/ca.pem"
                        docker-machine ssh "$2" service docker restart
                        if [[ -n "$(docker-machine ssh "$2" docker ps -aq)" ]]; then
                            docker-machine ssh "$2" "docker start \$(docker ps -aq)"
                        fi
                    fi

                    docker-machine ls
                fi
            else
                echo "The given Docker Machine name ($2) does not exists in your filesystem"
            fi
        else
            echo 'A machine name param after action is needed to use this action'
        fi
    elif [[ "$action" == 'deploy' ]]; then
        echo 'Docker Machine deploy:'
        if [[ "$#" -gt 1 ]] && [[ -n "$2" ]]; then
            count=$(find .docker -maxdepth 1 -name '*.yml' 2>/dev/null |wc -l |xargs)
            if [[ $count -eq 0 ]]; then
                echo "You must run this command into root of rudo-based project to work"
            elif [[ -f ".docker/$2.yml" ]] && [[ "$3" == "--soft" ]]; then
                echo "Running deployment script using <$2> environment with soft deployment option"
                eval ".scripts/cloud.sh deploy $2 $3"
            elif [[ -f ".docker/$2.yml" ]]; then
                echo "Running deployment script using <$2> environment"
                eval ".scripts/cloud.sh deploy $2"
            else
                echo -n "You've selected an invalid option. Available options: "
                options=""
                dirs=$(find .docker -maxdepth 1 -name '*.yml' 2>/dev/null)
                for entry in $dirs;
                do
                    options+="$(basename "$entry" .yml) "
                done
                echo "$options"
            fi
        else
            echo "A deploy environment param after action is needed to use this action"
        fi
    elif [[ "$action" == 'migrate' ]]; then
        echo 'Docker web container migrate action:'
        if [[ "$#" -gt 1 ]] && [[ -n "$2" ]]; then
            count=$(find .docker -maxdepth 1 -name '*.yml' 2>/dev/null |wc -l |xargs)
            if [[ $count -eq 0 ]]; then
                echo "You must run this command into root of rudo-based project to work"
            elif [[ -f ".docker/$2.yml" ]]; then
                echo "Running deployment script with migration order using <$2> environment"
                eval ".scripts/cloud.sh migrate $2"
            else
                echo -n "You've selected an invalid option. Available options: "
                options=""
                dirs=$(find .docker -maxdepth 1 -name '*.yml' 2>/dev/null)
                for entry in $dirs;
                do
                    options+="$(basename "$entry" .yml) "
                done
                echo "$options"
            fi
        else
            echo "A deploy environment param after action is needed to use this action"
        fi
    elif [[ "$action" == 'cloud' ]]; then
        echo 'Docker Machine cloud sync:'
        count=$(find .docker -maxdepth 1 -name '*.yml' 2>/dev/null |wc -l |xargs)
        if [[ $count -eq 0 ]]; then
            echo "You must run this command into root of rudo-based project to work"
        else
            if [[ -z "$2" ]]; then
                python3 .scripts/cloud_sync.py
            else
                python3 .scripts/cloud_sync.py "$2" "$3"
            fi
        fi
    elif [[ "$action" == 'vars' ]]; then
        printenv |grep DOCKER_
    else
        echo "$usage"
    fi
}

main_func "$@"
