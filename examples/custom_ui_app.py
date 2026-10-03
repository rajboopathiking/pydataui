"""
PyDataUI Custom Styling & Components Showcase.
Demonstrates:
  1. Built-in shadcn/ui components with custom palettes (violet, slate, blue, etc.)
  2. Tailwind CSS utility styling on all components
  3. Semantic HTML tags (Header, Nav, Section, Div, Span, Svg, Path, etc.)
  4. Raw HTML embedding (Html/RawHtml)
  5. Custom state reactivity without client-side JavaScript
"""
from pydataui import App, State, Html
from pydataui.html import Div, Span, Section, Header, Main, Footer, Nav, Svg, Path, H1, H2, P, A
from pydataui.components.shadcn import (
    ShadCard, ShadCardHeader, ShadCardTitle, ShadCardDescription,
    ShadCardContent, ShadCardFooter, ShadButton, ShadBadge, ShadInput,
    ShadSwitch, ShadProgress, ShadSeparator
)

class CustomShowcaseState(State):
    user_name: str = ""
    power_level: int = 42
    status_text: str = "Ready"
    turbo_mode: bool = False

    def boost_power(self):
        self.power_level = min(100, self.power_level + 15)
        self.status_text = f"Power boosted to {self.power_level}%!"

    def reset_power(self):
        self.power_level = 10
        self.status_text = "Power reset to base level."

    def toggle_turbo(self):
        self.turbo_mode = not self.turbo_mode
        self.status_text = "Turbo mode activated!" if self.turbo_mode else "Turbo mode deactivated."


app = App(
    title="Custom UI Showcase",
    theme="dark",
    palette="violet",
    tailwind_config={
        "theme": {
            "extend": {
                "colors": {
                    "glow": "#a855f7"
                }
            }
        }
    }
)

@app.page("/")
def home():
    return Section(
        # 1. Semantic Header with SVG Icon & Tailwind Backdrop Blur
        Header(
            Nav(
                Div(
                    Svg(
                        Path(d="M13 10V3L4 14h7v7l9-11h-7z"),
                        viewBox="0 0 24 24",
                        fill="currentColor",
                        class_name="w-6 h-6 text-glow"
                    ),
                    Span("PyDataUI Studio", class_name="font-black text-xl tracking-tight text-foreground"),
                    class_name="flex items-center gap-3"
                ),
                Div(
                    ShadBadge("v0.2.0 • Violet Palette", variant="secondary", class_name="font-mono text-xs"),
                    class_name="flex items-center gap-2"
                ),
                class_name="max-w-6xl mx-auto flex items-center justify-between p-4"
            ),
            class_name="sticky top-0 z-40 bg-card/60 backdrop-blur-xl border-b border-border"
        ),

        # 2. Main Content Area
        Main(
            # Hero Section
            Div(
                H1("Unlimited Customization", class_name="text-4xl font-extrabold tracking-tight sm:text-5xl text-foreground"),
                P("Tailwind CSS utility classes, shadcn/ui design tokens, semantic HTML, and zero client JS.",
                  class_name="text-muted-foreground mt-3 text-lg max-w-2xl mx-auto"),
                class_name="text-center my-10"
            ),

            # Grid with shadcn Cards + Custom Styling
            Div(
                # Card 1: Reactive State & shadcn Controls
                ShadCard(
                    ShadCardHeader(
                        ShadCardTitle("Reactivity & shadcn Controls"),
                        ShadCardDescription("Live HTMX updates driven by pure Python state."),
                    ),
                    ShadCardContent(
                        Div(
                            Div(
                                Span("Power Level:", class_name="text-sm font-medium text-foreground"),
                                Span(CustomShowcaseState.power_level, class_name="font-mono font-bold text-glow"),
                                class_name="flex justify-between items-center mb-2"
                            ),
                            ShadProgress(value=CustomShowcaseState.power_level),
                            class_name="mb-6"
                        ),
                        Div(
                            ShadButton("Boost +15%", variant="default", on_click=CustomShowcaseState.boost_power),
                            ShadButton("Reset", variant="outline", on_click=CustomShowcaseState.reset_power),
                            class_name="flex gap-3"
                        ),
                        Div(
                            Span("Status: ", class_name="text-xs text-muted-foreground"),
                            Span(CustomShowcaseState.status_text, class_name="text-xs font-semibold text-foreground"),
                            class_name="mt-4 p-2.5 rounded-lg bg-muted/50 border border-border"
                        )
                    ),
                    class_name="border-border shadow-lg"
                ),

                # Card 2: Custom HTML & SVG Embedding
                ShadCard(
                    ShadCardHeader(
                        ShadCardTitle("Custom HTML & SVG"),
                        ShadCardDescription("Directly embed any markup or vector graphics."),
                    ),
                    ShadCardContent(
                        Html("""
                        <div class="p-5 rounded-xl bg-gradient-to-br from-violet-600/20 via-purple-600/10 to-transparent border border-violet-500/30">
                            <div class="flex items-center gap-3">
                                <div class="w-10 h-10 rounded-lg bg-violet-600 flex items-center justify-center text-white shadow-lg shadow-violet-500/30">
                                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                                    </svg>
                                </div>
                                <div>
                                    <h4 class="font-semibold text-sm text-foreground">Hardware Accelerated SSR</h4>
                                    <p class="text-xs text-muted-foreground">Powered by Tokio + Hyper Rust backend</p>
                                </div>
                            </div>
                        </div>
                        """),
                        Div(
                            ShadSeparator(class_name="my-4"),
                            ShadSwitch(
                                checked=CustomShowcaseState.turbo_mode,
                                label="Enable Turbo Acceleration",
                                on_change=CustomShowcaseState.toggle_turbo
                            ),
                            class_name="flex flex-col gap-2"
                        )
                    ),
                    class_name="border-border shadow-lg"
                ),

                class_name="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-6 px-4"
            ),
            class_name="pb-16"
        ),

        # 3. Semantic Footer
        Footer(
            P("Crafted with PyDataUI • Rust Core + HTMX SSR + Tailwind CSS + shadcn/ui",
              class_name="text-xs text-muted-foreground text-center"),
            class_name="border-t border-border p-6 bg-card/40"
        ),

        class_name="min-h-screen bg-background flex flex-col justify-between"
    )

if __name__ == "__main__":
    app.run(port=8080)
