from fastapi import Request
from fastapi.templating import Jinja2Templates

class CalculatorView:
    def __init__(self):
        """ Initializes Jinja2Templates with the specified directory. """
        self.templates = Jinja2Templates(directory="NPICalculator/static")

    @property
    def template_name(self):
        """ Dynamically derives the template name from the class name. """
        return f"{self.__class__.__name__.lower().replace('view', '')}.html"

    def render(self, request, response):
        """ Renders a template with the provided request and context. """
        return self.templates.TemplateResponse(self.template_name, {"request": request, **response})

class IndexView(CalculatorView):
    def render(self, request: Request, message = "", icon = "info"):
        """ Renders a template for home page (welcoming and computing). """
        return super().render(request, {"message": message, "icon" : icon})

class ResultsView(CalculatorView):
    def render(self, request: Request, results):
        """ Renders a template for operations history (with possibly downloading in CSV). """
        return super().render(request, {"results": results})