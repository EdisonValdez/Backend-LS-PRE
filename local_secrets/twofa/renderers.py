from rest_framework import renderers


class SVGRenderer(renderers.BaseRenderer):
    media_type = 'image/svg+xml'
    format = 'svg'
    render_style = 'binary'

    def render(self, data, media_type=None, renderer_context=None):
        return data
