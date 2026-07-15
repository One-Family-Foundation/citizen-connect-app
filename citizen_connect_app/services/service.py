class ServiceManager:

    @staticmethod
    def get(limit=10, offset=0) -> Result:
        try:
            # 1. Validate and convert pagination values

            # 2. Define reusable filters
            #    - Service Status = Approved
            #    - Availability Status = Active

            # 3. Define the list of required fields

            # 4. Fetch records using the common database API
            #    - Apply filters
            #    - Apply selected fields
            #    - Order by creation DESC
            #    - Apply limit and offset

            # 5. Return success response
            #    - services
            #    - limit
            #    - offset
            #    - has_more

        except Exception as e:
            # Log the error

            # Return failure response