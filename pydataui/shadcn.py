"""
shadcn/ui design system components for PyDataUI.
Re-exports all shadcn/ui components, layout shells, precision ML controls,
and the universal extensibility engine.
"""
from .components.shadcn import (
    # Core primitives
    ShadButton,
    ShadCard,
    ShadCardHeader,
    ShadCardTitle,
    ShadCardDescription,
    ShadCardContent,
    ShadCardFooter,
    ShadInput,
    ShadCheckbox,
    ShadBadge,
    ShadAlert,
    ShadSeparator,
    ShadProgress,
    ShadSkeleton,
    ShadSwitch,
    ShadTable,
    ShadSelect,
    ShadTextarea,
    ShadLabel,
    ShadDialog,
    ShadScrollArea,
    ShadTabs,
    ShadToast,
    ShadAvatar,
    ShadHoverCard,
    ShadAccordion,
    ShadSheet,

    # Sidebar System & Responsive Shell
    ShadSidebarProvider,
    ShadSidebar,
    ShadSidebarHeader,
    ShadSidebarContent,
    ShadSidebarGroup,
    ShadSidebarGroupLabel,
    ShadSidebarMenu,
    ShadSidebarMenuItem,
    ShadSidebarMenuButton,
    ShadSidebarFooter,
    ShadSidebarRail,
    ShadSidebarTrigger,

    # High-Level Composable Dashboard Shells
    Sidebar,
    Header,
    DashboardLayout,
    NavGroup,
    NavItem,

    # Breadcrumbs
    ShadBreadcrumb,
    ShadBreadcrumbList,
    ShadBreadcrumbItem,
    ShadBreadcrumbLink,
    ShadBreadcrumbPage,
    ShadBreadcrumbSeparator,

    # Overlays, Menus & Dialogs
    ShadDropdownMenu,
    ShadDropdownItem,
    ShadDropdownSeparator,
    ShadDropdownLabel,
    ShadPopover,
    ShadTooltip,
    ShadAlertDialog,
    ShadCommandPalette,

    # ML & Precision Controls
    ShadSlider,
    ShadRadioGroup,
    ShadDatePicker,
    ShadPagination,

    # Component Factory
    create_shadcn_component,
    LUCIDE_ICONS,
)

from .components.parser import (
    from_jsx,
    from_html,
    dynamic,
    ParsedComponent,
)

__all__ = [
    # Core primitives
    'ShadButton',
    'ShadCard',
    'ShadCardHeader',
    'ShadCardTitle',
    'ShadCardDescription',
    'ShadCardContent',
    'ShadCardFooter',
    'ShadInput',
    'ShadCheckbox',
    'ShadBadge',
    'ShadAlert',
    'ShadSeparator',
    'ShadProgress',
    'ShadSkeleton',
    'ShadSwitch',
    'ShadTable',
    'ShadSelect',
    'ShadTextarea',
    'ShadLabel',
    'ShadDialog',
    'ShadScrollArea',
    'ShadTabs',
    'ShadToast',
    'ShadAvatar',
    'ShadHoverCard',
    'ShadAccordion',
    'ShadSheet',

    # Sidebar System & Responsive Shell
    'ShadSidebarProvider',
    'ShadSidebar',
    'ShadSidebarHeader',
    'ShadSidebarContent',
    'ShadSidebarGroup',
    'ShadSidebarGroupLabel',
    'ShadSidebarMenu',
    'ShadSidebarMenuItem',
    'ShadSidebarMenuButton',
    'ShadSidebarFooter',
    'ShadSidebarRail',
    'ShadSidebarTrigger',

    # High-Level Composable Dashboard Shells
    'Sidebar',
    'Header',
    'DashboardLayout',
    'NavGroup',
    'NavItem',

    # Breadcrumbs
    'ShadBreadcrumb',
    'ShadBreadcrumbList',
    'ShadBreadcrumbItem',
    'ShadBreadcrumbLink',
    'ShadBreadcrumbPage',
    'ShadBreadcrumbSeparator',

    # Overlays, Menus & Dialogs
    'ShadDropdownMenu',
    'ShadDropdownItem',
    'ShadDropdownSeparator',
    'ShadDropdownLabel',
    'ShadPopover',
    'ShadTooltip',
    'ShadAlertDialog',
    'ShadCommandPalette',

    # ML & Precision Controls
    'ShadSlider',
    'ShadRadioGroup',
    'ShadDatePicker',
    'ShadPagination',

    # Component Factory & Extensibility
    'create_shadcn_component',
    'from_jsx',
    'from_html',
    'dynamic',
    'ParsedComponent',
    'LUCIDE_ICONS',
]
