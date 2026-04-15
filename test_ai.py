import json
import os
import sys

# Add project root to sys.path
sys.path.append(r'c:\Users\mukil anand\OneDrive\Desktop\fake job detection')

from core.ai_engine import FraudDetector

text = """
Engineering
Analyst Trainee – Job Description
Work you’ll do 
Analyst trainees at Deloitte are expected to develop strong technical skills in the system/technology/area they work in. As a part of the project onboarding process, you will be provided with training/awareness aimed at building proficiency in the role. It involves the development of technical and behavioral skills as per defined proficiency levels (as per the Expectation Framework), understanding of the organization-specific tools and methodologies, and focused capability building on communication excellence
The Technology team offers both advisory and implementation services that provide clients with state-of-the-art solutions to help them better manage the critical business of information technology. As an Analyst Trainee, you may work on the below areas:
Support in delivery of a specific technology capability 
Understand business requirements and needs
Support technical/functional/process document creation and maintain an effective library
Help building, testing, and providing insights 
Support application design
Responsible for technical specification creation
Responsible for code development and unit testing
Responsible for test data creation, test scripts creation, and execution
Support infrastructure-building activities
Adhere to defined processes and tools while performing day-to-day operations
Help in developing and/or validating statistical models (financial risk models) for clients using various tools and techniques
Apply analytical skills to perform quantitative and qualitative assessment of the model design, data, estimation techniques, and performance

Our purpose
Deloitte’s purpose is to make an impact that matters for our people, clients, and communities. At Deloitte, purpose is synonymous with how we work every day. It defines who we are. Our purpose comes through in our work with clients that enables impact and value in their organizations, as well as through our own investments, commitments, and actions across areas that help drive positive outcomes for our communities.

Our people and culture
Our inclusive culture empowers our people to be who they are, contribute their unique perspectives, and make a difference individually and collectively. It enables us to leverage different ideas and perspectives, and bring more creativity and innovation to help solve our clients’ most complex challenges. This makes Deloitte one of the most rewarding places to work.

Professional development
At Deloitte, professionals have the opportunity to work with some of the best and discover what works best for them. Here, we prioritize professional growth, offering diverse learning and networking opportunities to help accelerate careers and enhance leadership skills. Our state-of-the-art DU: The Leadership Center in India, located in Hyderabad, represents a tangible symbol of our commitment to the holistic growth and development of our people. Explore DU: The Leadership Center in India.

Benefits to help you thrive
At Deloitte, we know that great people make a great organization. Our comprehensive rewards program helps us deliver a distinctly Deloitte experience that empowers our professionals to thrive mentally, physically, and financially—and live their purpose. To support our professionals and their loved ones, we offer a broad range of benefits. Eligibility requirements may be based on role, tenure, type of employment, and/or other criteria. Learn more about what working at Deloitte can mean for you.

Recruiting tips
From developing a standout resume to putting your best foot forward in the interview, we want you to feel prepared and confident as you explore opportunities at Deloitte. Check out recruiting tips from Deloitte recruiters.
"""


def main():
    detector = FraudDetector()
    result = detector.analyze(text)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
