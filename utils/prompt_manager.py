import json

class PromptManager():

    def __init__(self):
        with open("utils/categories.json", "r") as f:
            self.category_dict = json.load(f)

    def get_user_in_message(
            self,
            title,
            domain,
            category,
            subcategory,
            further_subcategory
    ):
        return json.dumps({
            "title": title,
            "domain": domain,
            "category": category,
            "subcategory": subcategory,
            "further_subcategory": further_subcategory,
            "useful_info": {
                "opts_fursub": self.category_dict[domain][category][subcategory],
                "opts_sub": list(self.category_dict[domain][category].keys()),
                "opts_cat": list(self.category_dict[domain].keys()),
                "opts_domain": list(self.category_dict.keys())
            }
        }, ensure_ascii = False)

    
    @staticmethod
    def system_prompts(chart):

        system_prompts = {
            "products": """
        You are an assistant data analysist, and you are assigned with a task of 'verifying the correctness of the categorization of e-commerce product data. All you have to do is to determine whether the current classification is precise and correct. 

        [Content Requirements]
        1. Logics:
            - Each product has four levels of categorization: domain, category, subcategory, and further subcategory. First judge whether the current further subcategory is correct. If not, try to suggest one in the available options of further subcategories under the current subcategory.
            - If you fail to find the suggested further subcategories, go up a level to search for a suggested subcategory under the current category. 
            - If you fail again, go up a level again to search for a suggested category within the available option pool.
            - If you fail again, go up a level again to search for a suggested domain within the available option pool.
            - If you fail eventually, just return "N/A" in the suggested domain column
        2. Factual Based: The whole analysis should be based entirely on the title of the product provided. No other reference data source is required.
        3. Do not come up with new categories in any level

        [Technical Requirements]
        1. For the quotation marks of JSON dict, use ". If including any quotation marks inside the JSON string, use ' rather than " to avoid JSON decode error. 
        2. Only output JSON body. No other texts are allowed.

        [Input Schema] You would be given:
        1. product name
        2. current product category in the following format: [domain, category / subcategory / further subcategory]
        3. available options of further subcategories under current subcategory
        4. available options of subcategories under current category
        5. available options of categories under current domain
        6. available options of domains
        in the following format:
            {{
            "title": (1),
            "domain": (2 - domain),
            "category": (2 - category),
            "subcategory": (2 - subcategory),
            "further_subcategory": (2 - further subcategory),
            "useful_info": {{
                    "opts_fursub": (3),
                    "opts_sub": (4),
                    "opts_cat": (5),
                    "opts_domain": (6)
                }}
            }}

        [Output Schema] You are required to output ONLY the JSON format as follows:
            {{
            "is_correct": [BOOL] (whether the current classification is correct),
            "suggested_domain": [STRING] (return current domain if is_correct == True, return the current domain if you successfully find a suggested category, return the suggested domain if you fail to find a suggested category, return 'TBD' if you fail again to find the suggested domain),
            "suggested_category": [STRING] (return current category if is_correct == True, return the current category if you successfully find a suggested subcategory, return the suggested category if you fail to find a suggested subcategory, return 'TBD' if you fail again to find the suggested category),
            "suggested_subcategory": [STRING] (return current subcategory if is_correct == True, return the current subcategory if you successfully find a suggested further subcategory, return the suggested subcategory if you fail to find a suggested further subcategory, return 'TBD' if you fail again to find the suggested subcategory),
            "suggested_further_subcategory": [STRING] (return current further subcategory if is_correct == True, return TBD if you fail to find a further subcategory),
            "confidence": [float] (the confidence of your judgement. range from 0 to 1),
            "reasoning"" [STRING] (not exceeding 30 words. only required when the current categorization is incorrect, so return N/A if is_correct == True.)
            }}

        """,
            "reference": """
        """
        }

        return system_prompts[chart]

