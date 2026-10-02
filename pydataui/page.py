from typing import Callable, Dict, List, Optional

class PageRoute:
    """Represents a registered page."""
    def __init__(
        self, 
        path: str, 
        handler: Callable, 
        title: Optional[str] = None, 
        layout: Optional[Callable] = None, 
        meta: Optional[Dict[str, str]] = None
    ):
        self.path = path
        self.handler = handler
        self.title = title
        self.layout = layout
        self.meta = meta or {}

class PageRouter:
    """Manages page routes."""
    def __init__(self):
        self._routes: Dict[str, PageRoute] = {}
        
    def add_page(
        self, 
        path: str, 
        handler: Callable, 
        title: Optional[str] = None, 
        layout: Optional[Callable] = None, 
        meta: Optional[Dict[str, str]] = None
    ) -> None:
        self._routes[path] = PageRoute(path, handler, title, layout, meta)
        
    def get_page(self, path: str) -> Optional[PageRoute]:
        return self._routes.get(path)
        
    def get_all_pages(self) -> List[PageRoute]:
        return list(self._routes.values())
