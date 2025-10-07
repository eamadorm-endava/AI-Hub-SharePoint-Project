# Image Extractor Module

This module provides a robust and extensible framework for extracting the main image URL from various news article web pages. It is designed to be efficient, easy to maintain, and simple to extend with new website extractors.

## Problems solved
Extracting specific data from different websites often leads to repetitive and difficult-to-maintain code. Without a proper design, a project can face several issues:

- **Code Duplication:** 

    The logic for downloading a web page, handling network errors, setting headers, and parsing HTML is repeated for each new website scraper, violating the DRY (Don't Repeat Yourself) principle.

- **Inconsistent Interfaces:** 
    
    Each scraper might have different method names and usage patterns, making them difficult to use interchangeably in a larger system.

- **Maintenance Difficulties:**
    
    If a common element needs to change (like updating the User-Agent header or improving the network error logging), the change must be manually applied to every single scraper file.

- **Difficult Extensibility:** 

    Adding a scraper for a new website is cumbersome and error-prone, as it requires copying and pasting boilerplate code instead of focusing on the unique parsing logic.

## Design Pattern Implemented: The *Template* Method

This module solves the problem by implementing the Template Method design pattern. This pattern uses an abstract base class to define the skeleton of an operation, while allowing subclasses to redefine certain steps of the algorithm without changing its overall structure.

It works like a recipe blueprint: the blueprint defines the main steps ("1. Prepare ingredients", "2. Cook", "3. Serve"), but the specific details of how to prepare and cook are left to specialized recipes (e.g., for pasta or salad).

### How it's Implemented Here
**BaseImageExtractor** (The Abstract Blueprint)
This class defines the complete, fixed workflow for extracting an image. It is responsible for all the common tasks:

- Defining the main public method, extract(), which acts as the "template."

- Downloading the HTML from a URL and handling network errors (_get_html_code).

- Caching the downloaded HTML to avoid redundant network requests.

- Defining the abstract "contract" method, _get_image_link(), which forces subclasses to implement their specific logic.

### Concrete Extractors (The Specialized Recipes)
Classes like **MITImageExtractor** and **AINEWSImageExtractor** inherit from BaseImageExtractor. 

Their only responsibility is to provide a concrete implementation for the _get_image_link() method. They focus exclusively on the unique task of parsing the HTML structure of their target website, leaving all the boilerplate logic to the parent class.
