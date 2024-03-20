# generate_docs.py

def run():
    print("Generating HTML documentation for views...")

    # Importing necessary modules for documentation generation
    from pydoc import HTMLDoc
    import os

    # Since we're running this script within Django's context thanks to 'runscript',
    # Django should already be fully initialized.
    # Here, we import the views for which we want to generate documentation.
    from api import views  # Adjust 'api.views' to the correct path of your views module

    # Generating HTML documentation
    doc = HTMLDoc().docmodule(views)

    # Define the path and name for the HTML file
    # You might want to adjust the directory according to your project structure
    html_file_path = os.path.join('docs', 'views_doc.html')
    os.makedirs(os.path.dirname(html_file_path), exist_ok=True)

    # Writing the generated documentation to an HTML file
    with open(html_file_path, 'w', encoding='utf-8') as html_file:
        html_file.write(doc)

    print(f"HTML documentation generated successfully: {html_file_path}")
