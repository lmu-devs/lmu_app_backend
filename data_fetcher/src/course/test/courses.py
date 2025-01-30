import requests
import json
from typing import List, Dict

class LMUCourseScraper:
    def __init__(self):
        self.base_url = "https://cms-search.lmu.de/search/courses_by_name_asc/execute"
        self.headers = {
            "Accept": "application/json",
            "Origin": "https://www.lmu.de",
            "Referer": "https://www.lmu.de/",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
            "Authorization": "Basic aGF1cGlhX3NlYXJjaF9wcm94eUBsbXUuZGU6aGF1cGlhX3NlYXJjaF9wcm94eQ=="
        }

    def fetch_courses(self, page: int = 1, num_rows: int = None) -> List[Dict]:
        """
        Fetch courses from the LMU API
        
        Args:
            page (int): Page number to fetch
            num_rows (int): Number of results per page. If None, will first fetch to determine total.
                
        Returns:
            List[Dict]: List of course dictionaries
        """
        # First fetch to get total number of rows if num_rows not specified
        if num_rows is None:
            initial_params = {
                "query": "*",
                "language": ["de", "en"],
                "page": 1,
                "numRows": 1
            }
            
            try:
                response = requests.get(
                    self.base_url,
                    params=initial_params,
                    headers=self.headers
                )
                response.raise_for_status()
                data = response.json()
                total_results = data.get("totalResults", 50)  # Get total number of results
                num_rows = total_results  # Set num_rows to fetch all results at once
                print(f"Debug - API Response: {json.dumps(data, indent=2)}")
                print(f"Debug - Total Results: {total_results}")
                print(f"Debug - Will fetch with num_rows: {num_rows}")
            except requests.RequestException as e:
                print(f"Error fetching total rows: {e}")
                num_rows = 50  # Default to 50 if request fails

        params = {
            "query": "*",
            "language": ["de", "en"],
            "page": page,
            "numRows": num_rows
        }

        try:
            response = requests.get(
                self.base_url,
                params=params,
                headers=self.headers
            )
            response.raise_for_status()
            
            data = response.json()
            return data.get("results", [])

        except requests.RequestException as e:
            print(f"Error fetching data: {e}")
            return []

    def extract_course_info(self, course: Dict) -> Dict:
        """
        Extract relevant information from a course dictionary
        
        Args:
            course (Dict): Course data dictionary
            
        Returns:
            Dict: Extracted course information
        """
        return {
            "name": course.get("Name_value", [None])[0],
            "degree": course.get("Degree_of_completion_value", [None])[0],
            "language": course.get("Language_value", [None])[0],
            "ects": course.get("ECTS_value", [None])[0],
            "type": course.get("Type_value", [None])[0],
            "start_of_studies": course.get("Start_of_studies_value", [None])[0],
            "teaching_language": course.get("teachingLanguage_value", [None])[0],
            "standard_period": course.get("standardPeriodOfStudy_value", [None])[0],
        }
        
def main():
    scraper = LMUCourseScraper()
    courses = scraper.fetch_courses()  # Will automatically fetch total number of rows
    
    if courses:
        print(f"\nSuccessfully fetched {len(courses)} courses")
        # Process and print each course
        for course in courses:
            course_info = scraper.extract_course_info(course)
            print("\nCourse Information:")
            for key, value in course_info.items():
                print(f"{key}: {value}")
    
    # Optionally save to JSON file
    with open("lmu_courses.json", "w", encoding="utf-8") as f:
        json.dump(courses, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()