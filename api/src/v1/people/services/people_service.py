from shared.src.services.directus_service import DirectusService
from ..models.people_model import People


class PeopleService:
    def __init__(self, language_code: str):
        self.directus = DirectusService()
        self.language_code = language_code

    async def get_people_by_faculty(self, faculty_id: str) -> People:
        query = """
        query PeopleByFaculty($facultyId: String!, $languageCode: String!) {
            people(filter: { faculty_id: { _eq: $facultyId } }) {
                id
                first_name
                last_name
                role
                email
            }
        }
        """
        variables = {
            "facultyId": faculty_id,
            "languageCode": self.language_code,
        }
        response = await self.directus.execute_graphql(query, variables)
        return People(root=response["data"]["people"])