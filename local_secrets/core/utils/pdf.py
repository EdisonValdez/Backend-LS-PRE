import io
import os

from django.conf import settings
from django.contrib.staticfiles import finders
from django.core.files.images import get_image_dimensions
from django.http import HttpResponse
from django.template.loader import get_template
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.styles import ListStyle, ParagraphStyle
from reportlab.platypus import (
    Image,
    ImageAndFlowables,
    ListFlowable,
    ListItem,
    Paragraph,
    ParagraphAndImage,
    SimpleDocTemplate,
    Spacer,
)
from xhtml2pdf import pisa

from local_secrets.sites.models import DefaultImage


def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources
    """
    result = finders.find(uri)
    if result:
        if not isinstance(result, (list, tuple)):
            result = [result]
        result = list(os.path.realpath(path) for path in result)
        path = result[0]
    else:
        sUrl = settings.STATIC_URL
        sRoot = settings.STATIC_ROOT
        mUrl = settings.MEDIA_URL
        mRoot = settings.MEDIA_ROOT

        if uri.startswith(mUrl):
            path = os.path.join(mRoot, uri.replace(mUrl, ""))
        elif uri.startswith(sUrl):
            path = os.path.join(sRoot, uri.replace(sUrl, ""))
        else:
            return uri

    # make sure that file exists
    if not os.path.isfile(path):
        raise Exception('media URI must start with %s or %s' % (sUrl, mUrl))
    return path


def generate_pdf_response_xhtml2pdf(travel, request, route=None):

    if route is None:
        template_path = 'pdf/template_django_pdf.html'

        context = {
            'user': travel.user,
            'username': travel.user.username,
            'travel': travel,
            'base_url': f'{request.scheme}://{request.get_host()}',
            "base_dir": settings.BASE_DIR,
        }
        filename = travel.title
    else:
        template_path = 'pdf/template_django_route_pdf.html'

        context = {
            'route': route,
            'base_url': f'{request.scheme}://{request.get_host()}',
            "base_dir": settings.BASE_DIR,
        }
        filename = route.title
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename={filename}'

    template = get_template(template_path)
    html = template.render(context)

    #   You can uncomment the next line to test the generated html
    # return HttpResponse(html)

    # create a pdf
    pisa.CreatePDF(html, dest=response, link_callback=link_callback)

    return response


def generate_pdf_response(travel):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename={travel.title}'

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, rightMargin=5, leftMargin=5, topMargin=5, bottomMargin=15)
    elements = []

    background_image = DefaultImage.objects.get(title='background').image
    dimensions = get_image_dimensions(background_image)
    elements.append(Image(background_image, height=doc.width * (dimensions[1] / dimensions[0]), width=doc.width))
    elements.append(
        Paragraph(
            travel.title,
            style=ParagraphStyle(name='Justify', alignement=TA_JUSTIFY, fontSize=18, fontName='Helvetica-Bold'),
        )
    )
    elements.append(Spacer(100, 30))

    icon_dimension = 12
    item_style = ListStyle(
        name='Item',
        alignement=TA_JUSTIFY,
        fontName='Helvetica',
        bulletColor=colors.white,
        hAlign='CENTER',
        vAlign='BOTTOM',
    )
    stops_list = []
    for stop in travel.stops.all():
        tags = stop.tags.all()
        tag_titles = ', '.join(list(tags.values_list('title', flat=True)))

        i_f = ImageAndFlowables(
            Image(stop.images.first().image, width=100, height=85),
            ListFlowable(
                [
                    ListItem(
                        Paragraph(
                            stop.title, style=ParagraphStyle(fontSize=12, fontName='Helvetica-Bold', name='Title')
                        )
                    ),
                    Spacer(5, 5),
                    ListItem(
                        ParagraphAndImage(
                            Paragraph(
                                f'{stop.address.street}, {stop.address.city.cp} {stop.address.city.name}, '
                                f'{stop.address.city.country.name}'
                            ),
                            Image(
                                DefaultImage.objects.get(title='location').image,
                                width=icon_dimension,
                                height=icon_dimension,
                            ),
                            side='left',
                        ),
                        style=item_style,
                    ),
                    Spacer(5, 5),
                    ListItem(
                        ParagraphAndImage(
                            Paragraph(tag_titles),
                            Image(
                                DefaultImage.objects.get(title='tags').image,
                                width=icon_dimension,
                                height=icon_dimension,
                            ),
                            side='left',
                        ),
                        style=item_style,
                    ),
                    Spacer(5, 5),
                    ListItem(
                        ParagraphAndImage(
                            Paragraph(f'{stop.url}'),
                            Image(
                                DefaultImage.objects.get(title='link').image,
                                width=icon_dimension,
                                height=icon_dimension,
                            ),
                            side='left',
                        ),
                        style=item_style,
                    ),
                    Spacer(5, 5),
                    ListItem(
                        ParagraphAndImage(
                            Paragraph(f'{stop.phone}'),
                            Image(
                                DefaultImage.objects.get(title='phone').image,
                                width=icon_dimension,
                                height=icon_dimension,
                            ),
                            side='left',
                        ),
                        style=item_style,
                    ),
                ],
                bulletColor=colors.white,
                hAlign='RIGHT',
                vAlign='BOTTOM',
            ),
            imageSide='left',
        )

        stops_list.append(i_f)
        stops_list.append(ListItem(Spacer(75, 75), backColor=colors.gray))

    stops_flowable = ListFlowable(
        stops_list, bulletColor='white', style=ListStyle(name='Background', backColor=colors.gray)
    )
    elements.append(stops_flowable)

    doc.build(elements)
    response.write(buffer.getvalue())
    buffer.close()
    return response
