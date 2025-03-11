import re
from datetime import date, datetime
from django.db import connection

def validateNationalId(nationalId, birthDate, gender):
    try:
        # initial validation
        if(len(nationalId) < 14): 
            return 2
        
        # validating the national id regex
        nationalIdRegex = r'^([2-3]{1})([0-9]{2})(0[1-9]|1[012])(0[1-9]|[1-2][0-9]|3[0-1])(0[1-4]|[1-2][1-9]|3[1-5]|88)[0-9]{3}([0-9]{1})[0-9]{1}$'
        nationalIdPattern = re.compile(nationalIdRegex)
        if(not re.fullmatch(nationalIdPattern, nationalId)):
            return 3

        # validating the date part
        datePart = nationalId[1:7]
        datePartString = f"{datePart[0:2]}-{datePart[2:4]}-{datePart[4:6]}"
        datePartDate = datetime.strptime(datePartString, "%y-%m-%d").date()
        # birthDate = datetime.strptime(birthDate, "%Y-%m-%d").date()
        if(birthDate != datePartDate):
            return 4
        
        # validating the gender part
        genderPart = int(nationalId[12:13])
        genderPartString = "Female" if(genderPart % 2 == 0) else "Male"
        if(genderPartString != gender):
            return 5
        return True
    except Exception as e:
        print(e)
        return 8