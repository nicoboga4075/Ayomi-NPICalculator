from fastapi import Request
from fastapi.templating import Jinja2Templates

class BaseView:
    def __init__(self):
        """ Initializes Jinja2Templates with the specified directory. 
        
        >>> view = BaseView()
        >>> isinstance(view.templates, Jinja2Templates)
        True

        """
        self.templates = Jinja2Templates(directory="NPICalculator/static")

    @property
    def template_name(self):
        """ Dynamically derives the template name from the class name.

        >>> base_view = BaseView()
        >>> base_view.template_name
        'base.html'

        >>> index_view = IndexView()
        >>> index_view.template_name
        'index.html'

        >>> results_view = ResultsView()
        >>> results_view.template_name
        'results.html'

        """
        return f"{self.__class__.__name__.lower().replace('view', '')}.html"

    def render(self, request, response):
        """ Renders a template with the provided request and response.
        
        >>> class MockRequest:
        ...     pass
        ...
        >>> class MockResponse(dict):
        ...     pass
        ...
        >>> view = BaseView()
        >>> response = MockResponse()
        >>> rendered = view.render(MockRequest(), response)
        >>> 'body' in rendered.body.decode()  # Checks if block content is included in response
        True

        """
        return self.templates.TemplateResponse(self.template_name, {"request": request, **response})

class IndexView(BaseView):
    def render(self, request: Request, message="", icon="info"):
        """ Renders a template for home page (welcoming and computing).
        
        >>> class MockRequest:
        ...     pass
        ...
        >>> view = IndexView()
        >>> response = {"message": "Hello !", "icon": "success"}
        >>> rendered = view.render(MockRequest(), **response)
        >>> 'Hello !' in rendered.body.decode()  # Checks if welcome message is included
        True
        >>> 'success' in rendered.body.decode()  # Checks if icon type is included
        True

        """
        return super().render(request, {"message": message, "icon": icon})

class ResultsView(BaseView):
    def render(self, request: Request, results):
        """ Renders a template for operations history (with possibly downloading in CSV).
        
        >>> class MockRequest:
        ...     pass
        ...
        >>> view = ResultsView()
        >>> mock_results = [{"expression": "3 4 +", "result": 7.0}, {"expression": "6 3 *", "result": 18.0}]
        >>> rendered = view.render(MockRequest(), mock_results)
        >>> any(str(result['result']) in rendered.body.decode() for result in mock_results)  # Checks if results are included
        True
        >>> len(rendered.body.decode()) > 0 # Checks if response body is not empty
        True

        """
        return super().render(request, {"results": results})