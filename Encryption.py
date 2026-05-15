import os
import base64
import zlib
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box
from rich.text import Text
import pyfiglet
from time import sleep

console = Console()

OUTPUT_PREFIX = "protected_"


# =========================
# SCREEN CLEAN SYSTEM
# =========================
def clear_screen():
    os.system("clear")


def boot_screen():
    clear_screen()
    console.print("[bold cyan]Starting HTML Protector Tool...[/bold cyan]")
    sleep(0.5)
    clear_screen()


# =========================
# OUTPUT FOLDER (OUTSIDE SAFE ROOT)
# =========================
def get_output_folder():
    base_path = Path("/sdcard")
    output_folder = base_path / "HTML_Protected_Files"
    output_folder.mkdir(exist_ok=True)
    return output_folder


# =========================
# HTML PROTECTION ENGINE
# =========================
def protect_html(html_code):
    compressed = zlib.compress(html_code.encode("utf-8"), level=9)
    encoded = base64.b64encode(compressed).decode()

    return f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Protected</title>
</head>

<body>

<script>

(function(){{

const data = "{encoded}";

async function decode(){{
    const binary = atob(data);
    const bytes = new Uint8Array(binary.length);

    for (let i = 0; i < binary.length; i++) {{
        bytes[i] = binary.charCodeAt(i);
    }}

    const stream = new DecompressionStream("deflate");
    const writer = stream.writable.getWriter();

    writer.write(bytes);
    writer.close();

    const buffer = await new Response(stream.readable).arrayBuffer();
    return new TextDecoder().decode(buffer);
}}

decode().then(html => {{
    document.open();
    document.write(html);
    document.close();
}});

}})();

</script>

</body>
</html>
"""


# =========================
# SCAN FULL STORAGE
# =========================
def get_html_files():
    search_path = Path("/sdcard")
    html_files = []

    try:
        for file in search_path.rglob("*"):
            if (
                file.is_file()
                and file.suffix.lower() in [".html", ".htm"]
                and not file.name.startswith(OUTPUT_PREFIX)
            ):
                html_files.append(file)

    except Exception as e:
        console.print(f"[red]Scan Error: {e}[/red]")

    return sorted(html_files, key=lambda x: x.name.lower())


# =========================
# BANNER
# =========================
def display_banner():
    banner = pyfiglet.figlet_format("HTML Protector", font="slant")
    console.print(Panel(Text(banner, style="bold cyan"), box=box.DOUBLE_EDGE))
    console.print(Panel("Advanced HTML Protection Tool", border_style="yellow"))


# =========================
# SIZE FORMAT
# =========================
def format_size(size):
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} TB"


# =========================
# STATS
# =========================
def display_stats(html_files):
    total_size = sum(f.stat().st_size for f in html_files)

    table = Table(title="📊 Storage Info", box=box.ROUNDED)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="yellow")

    table.add_row("📁 HTML Files", str(len(html_files)))
    table.add_row("💾 Total Size", format_size(total_size))
    table.add_row("📍 Scan Path", "/sdcard (FULL SCAN)")

    console.print(table)
    console.print()


# =========================
# FILE LIST (ONLY NAME)
# =========================
def display_files_table(html_files):
    if not html_files:
        console.print(Panel("[red]No HTML files found![/red]", box=box.HEAVY))
        return False

    table = Table(title="📄 HTML Files", box=box.HEAVY_EDGE)

    table.add_column("No.", justify="center", style="cyan")
    table.add_column("Filename", style="green")
    table.add_column("Size", justify="right", style="magenta")
    table.add_column("Status", style="white")

    for i, file in enumerate(html_files, 1):
        table.add_row(
            str(i),
            file.name,
            format_size(file.stat().st_size),
            "[green]✓ Found[/green]"
        )

    console.print(table)
    console.print()
    return True


# =========================
# PREVIEW
# =========================
def show_file_preview(file_path):
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")

        console.print(
            Panel(
                content[:500] + ("\n...\n[dim]Preview truncated[/dim]" if len(content) > 500 else ""),
                title=f"📖 Preview: {file_path.name}",
                border_style="magenta"
            )
        )
    except Exception as e:
        console.print(f"[red]Preview Error: {e}[/red]")


# =========================
# PROTECTION PROCESS
# =========================
def protect_with_animation(selected_file):
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:

        task = progress.add_task("Protecting file...", total=None)

        try:
            html_code = selected_file.read_text(encoding="utf-8", errors="ignore")

            progress.update(task, description="Compressing...")
            sleep(0.3)

            protected_html = protect_html(html_code)

            progress.update(task, description="Saving to external folder...")
            sleep(0.3)

            output_folder = get_output_folder()

            output_name = output_folder / f"{OUTPUT_PREFIX}{selected_file.stem}.html"

            output_name.write_text(protected_html, encoding="utf-8")

            progress.update(task, description="Done!")
            sleep(0.5)

            return output_name

        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            return None


# =========================
# RESULT
# =========================
def display_result(original, output):
    console.print(
        Panel(
            f"[bold green]SUCCESS! FILE PROTECTED[/bold green]\n\n"
            f"Input: {original.name}\n"
            f"Output: {output}",
            box=box.HEAVY,
            border_style="green"
        )
    )


# =========================
# MAIN
# =========================
def main():
    boot_screen()
    display_banner()

    html_files = get_html_files()

    display_stats(html_files)

    if not display_files_table(html_files):
        return

    choice = IntPrompt.ask(
        "Select file number",
        choices=[str(i) for i in range(1, len(html_files) + 1)]
    )

    selected_file = html_files[choice - 1]

    console.print(Panel(f"Selected: {selected_file.name}", border_style="blue"))

    if Prompt.ask("Show preview? (y/n)", default="n") == "y":
        show_file_preview(selected_file)

    if Prompt.ask("Protect file? (y/n)", default="y") != "y":
        return

    output = protect_with_animation(selected_file)

    if output:
        display_result(selected_file, output)


# =========================
# RUN
# =========================
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("[red]Exited[/red]")
