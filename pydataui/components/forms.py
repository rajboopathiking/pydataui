from __future__ import annotations
from typing import Any, List, Optional
from .base import Component
from .typography import Label
from ..utils import escape_html
from ..state import StateVarRef

class Button(Component):
    tag = 'button'
    def __init__(self, *children, variant='primary', size='md', disabled=False, loading=False, full_width=False, type='button', **props):
        super().__init__(*children, **props)
        self.variant = variant
        self.size = size
        self.props['type'] = type
        if disabled or loading:
            self.props['disabled'] = 'disabled'
        self.loading = loading
        self.full_width = full_width
        
    def _get_classes(self) -> List[str]:
        classes = super()._get_classes() + ['pdu-btn', f'pdu-btn-{self.variant}', f'pdu-btn-{self.size}']
        if self.full_width: classes.append('pdu-btn-full')
        if self.loading: classes.append('pdu-btn-loading')
        return classes

    @property
    def label(self) -> str:
        if self.children:
            return str(self.children[0])
        return str(self.props.get('label', ''))

    @property
    def on_click(self) -> Any:
        return self._event_props.get('on_click') or self.props.get('on_click')

class Input(Component):
    tag = 'input'
    def __init__(self, *args, type='text', placeholder='', value=None, name=None, bind=None, required=False, disabled=False, readonly=False, size='md', variant='outline', label=None, helper_text=None, error=None, on_change=None, on_input=None, **props):
        if args and label is None:
            label = args[0]
        if bind is None:
            bind = props.pop('bind', None)
        self.bind = bind
        if self.bind is not None:
            if isinstance(self.bind, StateVarRef):
                if name is None:
                    name = self.bind.field_name
                if value is None:
                    value = self.bind
        if name is None and label:
            name = str(label).lower().strip().replace(' ', '_')
        super().__init__(**props)
        self.props['type'] = type
        self.props['placeholder'] = placeholder
        if value is not None: self.props['value'] = value
        if name is not None: self.props['name'] = name
        if required: self.props['required'] = 'required'
        if disabled: self.props['disabled'] = 'disabled'
        if readonly: self.props['readonly'] = 'readonly'
        self.size = size
        self.variant = variant
        self.label = label
        self.helper_text = helper_text
        self.error = error

        # HTMX integration for inputs
        if on_change:
            self._event_props['on_change'] = on_change
            self.props['hx-trigger'] = self.props.get('hx-trigger', 'change')
            self.props['hx-include'] = self.props.get('hx-include', 'this')
        if on_input:
            self._event_props['on_input'] = on_input
            self.props['hx-trigger'] = self.props.get('hx-trigger', 'input delay:300ms')
            self.props['hx-include'] = self.props.get('hx-include', 'this')

    @property
    def placeholder(self) -> str:
        return self.props.get('placeholder', '')
            
    def _get_classes(self) -> List[str]:
        classes = super()._get_classes() + ['pdu-input', f'pdu-input-{self.size}', f'pdu-input-{self.variant}']
        if self.error: classes.append('pdu-input-error')
        return classes
        
    def render(self, state_snapshot: Optional[dict] = None) -> str:
        snap = state_snapshot or {}
        attrs = self._build_attrs(snap)
        input_html = f"<{self.tag} {attrs} />"
        
        if not self.label and not self.error and not self.helper_text:
            return input_html
            
        parts = []
        if self.label:
            parts.append(Label(self.label).render(snap))
        parts.append(input_html)
        if self.error:
            parts.append(f"<div class='pdu-error-text'>{escape_html(self.error)}</div>")
        elif self.helper_text:
            parts.append(f"<div class='pdu-helper-text'>{escape_html(self.helper_text)}</div>")
            
        return f"<div class='pdu-input-group'>{''.join(parts)}</div>"

class TextArea(Input):
    tag = 'textarea'
    def __init__(self, placeholder='', value=None, name=None, bind=None, rows=4, required=False, disabled=False, size='md', label=None, error=None, on_change=None, **props):
        super().__init__(type=None, placeholder=placeholder, value=value, name=name, bind=bind, required=required, disabled=disabled, size=size, label=label, error=error, on_change=on_change, **props)
        self.props['rows'] = rows
        self._value_content = self.props.pop('value', '')
        
    def _get_classes(self) -> List[str]:
        classes = super()._get_classes()
        if 'pdu-input' in classes: classes.remove('pdu-input')
        classes.append('pdu-textarea')
        return classes
        
    def render(self, state_snapshot: dict) -> str:
        attrs = self._build_attrs(state_snapshot)
        val = self._resolve_value(self._value_content, state_snapshot) or ''
        input_html = f"<{self.tag} {attrs}>{escape_html(str(val))}</{self.tag}>"
        
        if not self.label and not self.error and not self.helper_text:
            return input_html
            
        parts = []
        if self.label:
            parts.append(Label(self.label).render(state_snapshot))
        parts.append(input_html)
        if self.error:
            parts.append(f"<div class='pdu-error-text'>{escape_html(self.error)}</div>")
            
        return f"<div class='pdu-input-group'>{''.join(parts)}</div>"

class Select(Input):
    tag = 'select'
    def __init__(self, options=None, value=None, placeholder='Select...', name=None, required=False, disabled=False, multiple=False, size='md', label=None, error=None, on_change=None, **props):
        super().__init__(type=None, value=value, name=name, required=required, disabled=disabled, size=size, label=label, error=error, on_change=on_change, **props)
        self.options = options or []
        self.placeholder_text = placeholder
        self.multiple = multiple
        if multiple:
            self.props['multiple'] = 'multiple'
        self._selected_value = self.props.pop('value', None)
        
    def _get_classes(self) -> List[str]:
        classes = super()._get_classes()
        if 'pdu-input' in classes: classes.remove('pdu-input')
        classes.append('pdu-select')
        return classes
        
    def render(self, state_snapshot: dict) -> str:
        attrs = self._build_attrs(state_snapshot)
        selected_val = self._resolve_value(self._selected_value, state_snapshot)
        
        opts_html = []
        if self.placeholder_text and not self.multiple:
            opts_html.append(f"<option value='' disabled selected>{escape_html(self.placeholder_text)}</option>")
            
        for opt in self.options:
            if isinstance(opt, dict):
                v, l = opt.get('value', ''), opt.get('label', '')
            else:
                v, l = opt, opt
            sel = " selected" if str(v) == str(selected_val) else ""
            opts_html.append(f"<option value='{escape_html(str(v))}'{sel}>{escape_html(str(l))}</option>")
            
        input_html = f"<{self.tag} {attrs}>{''.join(opts_html)}</{self.tag}>"
        
        if not self.label and not self.error:
            return input_html
            
        parts = []
        if self.label: parts.append(Label(self.label).render(state_snapshot))
        parts.append(input_html)
        if self.error: parts.append(f"<div class='pdu-error-text'>{escape_html(self.error)}</div>")
            
        return f"<div class='pdu-input-group'>{''.join(parts)}</div>"

class Checkbox(Component):
    tag = 'label'
    def __init__(self, label='', checked=False, name=None, value=None, bind=None, disabled=False, on_change=None, **props):
        if bind is None:
            bind = props.pop('bind', None)
        self.bind = bind
        if self.bind is not None:
            if isinstance(self.bind, StateVarRef):
                if name is None:
                    name = self.bind.field_name
                checked = self.bind
        if name is None and label:
            name = str(label).lower().strip().replace(' ', '_')
        super().__init__(**props)
        self.label = label
        self.checked = checked
        self.input_props = {'type': 'checkbox'}
        if name is not None: self.input_props['name'] = name
        if value is not None: self.input_props['value'] = value
        if disabled: self.input_props['disabled'] = 'disabled'
        self.on_change = on_change
        if on_change:
            self.input_props['hx-trigger'] = 'change'
            self.input_props['hx-include'] = 'this'
            
    def _get_classes(self) -> List[str]:
        return super()._get_classes() + ['pdu-checkbox-wrapper']
        
    def render(self, state_snapshot: dict) -> str:
        attrs = self._build_attrs(state_snapshot)
        is_chk = self._resolve_value(self.checked, state_snapshot)
        inp_props = dict(self.input_props)
        if is_chk:
            inp_props['checked'] = 'checked'
        
        inp_attrs = []
        for k, v in inp_props.items():
            inp_attrs.append(f'{k}="{escape_html(str(v))}"')
        if self.on_change:
            htmx = self._get_event_htmx_attrs('on_change', self.on_change)
            for hk, hv in htmx.items():
                inp_attrs.append(f'{hk}="{escape_html(str(hv))}"')
                
        inp_html = f'<input class="pdu-checkbox" {" ".join(inp_attrs)} />'
        return f'<{self.tag} {attrs}>{inp_html}<span class="pdu-checkbox-label">{escape_html(self.label)}</span></{self.tag}>'

class Radio(Checkbox):
    def __init__(self, label='', name=None, value=None, checked=False, disabled=False, on_change=None, **props):
        super().__init__(label=label, checked=checked, name=name, value=value, disabled=disabled, on_change=on_change, **props)
        self.input_props['type'] = 'radio'
        
    def _get_classes(self) -> List[str]:
        classes = super()._get_classes()
        if 'pdu-checkbox-wrapper' in classes: classes.remove('pdu-checkbox-wrapper')
        classes.append('pdu-radio-wrapper')
        return classes

class RadioGroup(Component):
    tag = 'div'
    def __init__(self, options=None, name=None, value=None, direction='column', gap='sm', on_change=None, **props):
        super().__init__(**props)
        self.options = options or []
        self.name = name
        self.value = value
        self.direction = direction
        self.gap = gap
        self.on_change = on_change
        
    def _get_classes(self) -> List[str]:
        return super()._get_classes() + ['pdu-radio-group', f'pdu-flex-{self.direction}', f'pdu-gap-{self.gap}']
        
    def render(self, state_snapshot: dict) -> str:
        attrs = self._build_attrs(state_snapshot)
        selected = self._resolve_value(self.value, state_snapshot)
        
        radios = []
        for opt in self.options:
            if isinstance(opt, dict):
                v, l = opt.get('value', ''), opt.get('label', '')
            else:
                v, l = opt, opt
            checked = str(v) == str(selected)
            r = Radio(label=str(l), name=self.name, value=v, checked=checked, on_change=self.on_change)
            radios.append(r.render(state_snapshot))
            
        return f"<{self.tag} {attrs}>{''.join(radios)}</{self.tag}>"

class Switch(Checkbox):
    def __init__(self, label='', checked=False, name=None, disabled=False, on_change=None, **props):
        super().__init__(label=label, checked=checked, name=name, disabled=disabled, on_change=on_change, **props)
        
    def _get_classes(self) -> List[str]:
        classes = super()._get_classes()
        if 'pdu-checkbox-wrapper' in classes: classes.remove('pdu-checkbox-wrapper')
        classes.append('pdu-switch-wrapper')
        return classes

class Slider(Component):
    tag = 'div'
    def __init__(self, min=0, max=100, value=50, step=None, name=None, disabled=False, label=None, show_value=True, on_change=None, **props):
        super().__init__(**props)
        if step is None:
            if any(isinstance(v, float) for v in (min, max, value)):
                diff = abs(max - min)
                step = 0.01 if diff <= 1.0 else (0.1 if diff <= 10.0 else 0.01)
            else:
                step = 1
        self.min = min
        self.max = max
        self.value = value
        self.step = step
        self.name = name
        self.disabled = disabled
        self.label = label
        self.show_value = show_value
        self.on_change = on_change
        
    def _get_classes(self) -> List[str]:
        return super()._get_classes() + ['pdu-slider-wrapper']
        
    def render(self, state_snapshot: dict) -> str:
        attrs = self._build_attrs(state_snapshot)
        val = self._resolve_value(self.value, state_snapshot)
        
        inp_attrs = [
            "type='range'",
            f"min='{self.min}'",
            f"max='{self.max}'",
            f"step='{self.step}'",
            f"value='{val}'",
            "class='pdu-slider'",
            "data-pdu-slider='true'",
            "oninput=\"var v=this.parentNode.querySelector('.pdu-slider-value'); if(v) v.innerText = this.value;\"",
        ]
        if self.name: inp_attrs.append(f"name='{self.name}'")
        if self.disabled: inp_attrs.append("disabled")
        
        if self.on_change:
            inp_attrs.append("hx-trigger='change'")
            inp_attrs.append("hx-include='this'")
            htmx = self._get_event_htmx_attrs('on_change', self.on_change)
            for hk, hv in htmx.items():
                inp_attrs.append(f"{hk}='{escape_html(str(hv))}'")
                
        inp = f"<input {' '.join(inp_attrs)} />"
        
        parts = []
        if self.label or self.show_value:
            header = "<div class='pdu-slider-header'>"
            if self.label: header += f"<span class='pdu-slider-label'>{escape_html(self.label)}</span>"
            if self.show_value: header += f"<span class='pdu-slider-value'>{val}</span>"
            header += "</div>"
            parts.append(header)
        parts.append(inp)
        
        return f"<{self.tag} {attrs}>{''.join(parts)}</{self.tag}>"

class Form(Component):
    tag = 'form'
    def __init__(self, *children, on_submit=None, method='POST', action=None, **props):
        super().__init__(*children, **props)
        self.props['method'] = method
        if action: self.props['action'] = action
        if on_submit:
            self._event_props['on_submit'] = on_submit
            
    def _get_classes(self) -> List[str]:
        return super()._get_classes() + ['pdu-form']
        
    def render(self, state_snapshot: dict) -> str:
        if 'on_submit' in self._event_props:
            htmx = self._get_event_htmx_attrs('on_submit', self._event_props['on_submit'])
            # Override with hx-post for form submissions
            if 'hx-get' in htmx:
                htmx['hx-post'] = htmx.pop('hx-get')
            elif not any(k.startswith('hx-') for k in htmx if k in ('hx-post', 'hx-put', 'hx-patch', 'hx-delete')):
                ep = self._event_props['on_submit'].get_endpoint() if hasattr(self._event_props['on_submit'], 'get_endpoint') else ''
                htmx['hx-post'] = ep
            self.props.update(htmx)
            self.props['hx-trigger'] = 'submit'
            
        return super().render(state_snapshot)

    @classmethod
    def from_pydantic(cls, model_class: Any, on_submit: Optional[Any] = None, **kwargs) -> Component:
        """Auto-generate a validated form from a Pydantic model or dataclass."""
        from .shadcn import ShadForm
        return ShadForm.from_pydantic(model_class, on_submit=on_submit, **kwargs)


class LazyDataProxy:
    """
    Lazy proxy representing uploaded file data that resolves dynamically upon render.
    Allows procedural code like `pdu.write(dataset.get_data())` to bind cleanly
    before any file is uploaded, and automatically display the table once uploaded.
    """
    def __init__(self, uploader: Any):
        self._uploader = uploader

    def _resolve(self) -> Any:
        try:
            from ..dx import session_state
            k = getattr(self._uploader, "key", None) or getattr(self._uploader, "name", None) or self._uploader.props.get("name")
            val = session_state.get(k) if k else None
            if val is None:
                val = session_state.get("last_uploaded_file")
            if val is not None:
                if hasattr(val, "get_data"):
                    return val.get_data()
                if hasattr(val, "to_pandas"):
                    return val.to_pandas()
                return val
        except Exception:
            pass
        return None

    def __bool__(self) -> bool:
        return self._resolve() is not None

    def __getattr__(self, name: str) -> Any:
        res = self._resolve()
        if res is not None:
            return getattr(res, name)
        raise AttributeError(f"No file has been uploaded yet (cannot access '{name}'). Check 'if dataset:' first.")

    def __repr__(self) -> str:
        res = self._resolve()
        return repr(res) if res is not None else "<Empty FileUpload dataset>"


class FileUpload(Input):
    def __init__(self, name='file', accept=None, multiple=False, label='Choose file', on_change=None, **props):
        super().__init__(type='file', name=name, label=label, on_change=on_change, **props)
        if accept:
            if isinstance(accept, (list, tuple)):
                self.props['accept'] = ','.join(str(x) for x in accept)
            else:
                self.props['accept'] = str(accept)
        if multiple: self.props['multiple'] = 'multiple'
        self.props['hx-encoding'] = 'multipart/form-data'

    def get_data(self) -> Any:
        """Return a dynamic lazy proxy that resolves to the uploaded DataFrame / file data."""
        proxy = LazyDataProxy(self)
        res = proxy._resolve()
        return res if res is not None else proxy

    def to_pandas(self, **kwargs) -> Any:
        proxy = LazyDataProxy(self)
        res = proxy._resolve()
        if res is not None and hasattr(res, "to_pandas"):
            return res.to_pandas(**kwargs)
        return res

    to_dataframe = to_pandas

    def getvalue(self) -> Optional[bytes]:
        proxy = LazyDataProxy(self)
        res = proxy._resolve()
        if hasattr(res, "getvalue"):
            return res.getvalue()
        return None

    def __bool__(self) -> bool:
        return LazyDataProxy(self)._resolve() is not None

    def _get_classes(self) -> List[str]:
        classes = super()._get_classes()
        if 'pdu-input' in classes: classes.remove('pdu-input')
        classes.append('pdu-file-upload')
        return classes

    def render(self, state_snapshot: Optional[dict] = None) -> str:
        snap = state_snapshot or {}
        from ..dx import session_state
        k = getattr(self, "key", None) or getattr(self, "name", None) or self.props.get("name")
        uploaded = session_state.get(k) if k else None
        if uploaded is None:
            uploaded = session_state.get("last_uploaded_file")

        file_status_html = ""
        if uploaded is not None:
            fname = getattr(uploaded, "filename", "File uploaded")
            size = getattr(uploaded, "size", 0)
            size_kb = round(size / 1024, 1) if size else 0
            file_status_html = (
                f"<div class='mt-2 flex items-center gap-2 text-xs font-medium text-emerald-600 dark:text-emerald-400 bg-emerald-500/10 px-3 py-1.5 rounded-lg border border-emerald-500/20 shadow-xs'>"
                f"<span>✓</span><span>{escape_html(fname)} ({size_kb} KB)</span>"
                f"</div>"
            )

        base_html = super().render(snap)
        if file_status_html:
            return f"<div class='w-full'>{base_html}{file_status_html}</div>"
        return base_html
