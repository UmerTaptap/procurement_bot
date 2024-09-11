from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from difflib import get_close_matches
import logging
from rasa_sdk.types import DomainDict
import pandas as pd
from fuzzywuzzy import process


data = pd.read_csv('./data_file.csv')


logger = logging.getLogger(__name__)


# Sample data for procurements
PROCUREMENTS = [
    {
        "title": "Advisory for M&A, Separation, Divestment and Transformation",
        "skills": ["Transformation", "Divestment", "Mergers & Acquisitions", "Consulting"],
        "experience": [
            "Accenture",
            "Aster Group",
            "Aviva",
            "Carllyle Group",
            "IDH",
            "Dental Directory",
            "Francisco Partners",
            "Keyloop",
            "GSK",
            "James Fisher",
            "PwC",
            "TOTSCo",
            "UCL",
            "Virgin Care"
        ],
        "keywords": ["M&A", "Transformation", "Separation", "Divestment", "Consulting"],
        "industry": ["Healthcare", "Pharmaceutical", "Finance", "Consulting"],
        "sector": ["Private", "Public"],
        "challenges_addressed": ["M&A challenges", "Separation complexities", "Transformation of businesses"],
        "description": "Provided advisory services in Mergers, Acquisitions, Divestment and Business Transformation across various sectors."
    },
    {
        "title": "Navigating Human Rights across the Supply Chain",
        "skills": ["Human Rights", "Supply Chain", "Legal Compliance", "Procurement"],
        "experience": [
            "UK Government Cabinet Office",
            "Civil Aviation Authority",
            "High Court ruling EWHC1841",
            "Private sector procurement",
            "Africa joint venture distributor"
        ],
        "keywords": ["Human Rights", "Supply Chain", "Legal Compliance", "Accessibility", "Statutory Duty"],
        "industry": ["Public Sector", "Legal", "Procurement", "Aviation"],
        "sector": ["Public", "Private"],
        "challenges_addressed": ["Statutory duty discharge", "Supply chain human rights compliance"],
        "description": "Managed Freedom of Information requests and ensured compliance with human rights in supply chains, with global outreach."
    },
    {
        "title": "IT Procurement Process Improvement",
        "skills": ["IT Procurement", "Process Improvement", "Risk Reduction", "Supplier Management"],
        "experience": [
            "NHS Trust",
            "CIPS Distinction"
        ],
        "keywords": ["IT Procurement", "Process Optimization", "Risk Reduction", "Savings"],
        "industry": ["Healthcare", "IT"],
        "sector": ["Public", "Private"],
        "challenges_addressed": ["Procurement inefficiencies", "Risk in buying processes", "Cost savings"],
        "description": "Delivered an improved IT procurement strategy for an NHS Trust that resulted in better processes and cost savings."
    },
    {
        "title": "IT Procurement Sourcing Strategies for Public Sector",
        "skills": ["IT Procurement", "Sourcing Strategies", "Public Sector Procurement"],
        "experience": ["10 years in IT Procurement", "End-to-End Tendering", "Contract Management"],
        "keywords": ["IT Procurement", "Sourcing Strategies", "Contract Management"],
        "industry": ["Public Sector", "IT"],
        "sector": ["Public", "Private"],
        "challenges_addressed": ["Efficient tendering", "Managing IT contracts"],
        "description": "Provided expertise in sourcing strategies for IT procurement across both public and private sectors."
    },
    {
        "title": "Expert Creation of Excel-based Supply Chain KPI's/Dashboards",
        "skills": ["Excel", "KPI Development", "Supply Chain", "Dashboards"],
        "experience": ["Multiple clients in supply chain", "Inventory Management", "Cost Reduction"],
        "keywords": ["KPI", "Supply Chain", "Dashboards", "Inventory Management"],
        "industry": ["Supply Chain", "Logistics"],
        "sector": ["Private"],
        "challenges_addressed": ["Inventory optimization", "Cost reduction", "Supplier collaboration"],
        "description": "Developed Excel-based KPIs and dashboards that significantly improved supply chain performance for multiple clients."
    },
    {
        "title": "IT Procurement Programme Delivery",
        "skills": ["IT Procurement", "Programme Delivery", "Cybersecurity", "Enforcement Cameras"],
        "experience": ["Major Airport Cybersecurity", "Transport Company Enforcement Cameras"],
        "keywords": ["IT Procurement", "Programme Delivery", "Cybersecurity", "Transport"],
        "industry": ["Aviation", "Transport", "IT"],
        "sector": ["Public", "Private"],
        "challenges_addressed": ["Cybersecurity procurement", "Enforcement camera procurement"],
        "description": "Led commercial programmes in IT procurement for high-profile projects, including Cybersecurity and Enforcement Cameras."
    },
    {
        "title": "Software Licensing Impact During Mergers, Acquisition or Divestments",
        "skills": ["Software Licensing", "Mergers & Acquisitions", "Divestments"],
        "experience": ["Divestments negotiations", "Supplier Rationalization"],
        "keywords": ["Software Licensing", "M&A", "Divestments", "Supplier Rationalization"],
        "industry": ["IT", "Legal", "Consulting"],
        "sector": ["Private"],
        "challenges_addressed": ["Licensing impact during M&A", "Supplier rationalization"],
        "description": "Handled software licensing challenges during mergers, acquisitions, and divestments, including supplier rationalization."
    },
    {
        "title": "Advice on IT Outsourcing and Business Transformation",
        "skills": ["IT Outsourcing", "Business Transformation", "RFPs", "SLAs"],
        "experience": ["Outsourcing Agreements", "Management of Change"],
        "keywords": ["IT Outsourcing", "Business Transformation", "RFPs", "SLAs"],
        "industry": ["IT", "Consulting"],
        "sector": ["Private"],
        "challenges_addressed": ["Outsourcing alignment with business goals", "Change management"],
        "description": "Provided advice on IT outsourcing and business transformation, ensuring services aligned with business vision and objectives."
    },
    {
        "title": "IT Software Licensing and Asset Management",
        "skills": ["Software Licensing", "Asset Management", "Negotiation"],
        "experience": ["Multi-million pound negotiations", "Licensing cost reduction"],
        "keywords": ["Software Licensing", "Asset Management", "Negotiation"],
        "industry": ["IT", "Legal"],
        "sector": ["Private"],
        "challenges_addressed": ["Licensing cost control", "Supplier negotiations"],
        "description": "Led negotiations to manage software licensing, reducing costs and ensuring compliance with asset management strategies."
    },
    {
        "title": "How to Manage a Software Licensing Audit",
        "skills": ["Software Licensing", "Audit Management", "Negotiation"],
        "experience": ["Multi-million pound negotiations", "Audit Cost Reduction"],
        "keywords": ["Software Licensing", "Audit", "Negotiation"],
        "industry": ["IT", "Legal"],
        "sector": ["Private"],
        "challenges_addressed": ["Licensing audit management", "Cost reduction during audits"],
        "description": "Experienced in managing software licensing audits, negotiating with suppliers to reduce potential costs."
    },
]


class ProcurementSearcher:
    @staticmethod
    def search_procurements(title, skill, experience, keyword, industry, sector, challenge):
        results = []

        for procurement in PROCUREMENTS:
            match = False

            if sector and sector.lower() not in procurement.get('sector', []):
                continue

            if title:
                if title.lower() in procurement.get('title', '').lower():
                    match = True
            if not match and skill:
                if any(skill.lower() in s.lower() for s in procurement.get('skills', [])):
                    match = True
            if not match and experience:
                if any(experience.lower() in e.lower() for e in procurement.get('experience', [])):
                    match = True
            if not match and keyword:
                if any(keyword.lower() in k.lower() for k in procurement.get('keywords', [])):
                    match = True
            if not match and industry:
                if any(industry.lower() in i.lower() for i in procurement.get('industry', [])):
                    match = True
            if not match and challenge:
                if any(challenge.lower() in c.lower() for c in procurement.get('challenges_addressed', [])):
                    match = True
            if not match and not (title or skill or experience or keyword or industry or challenge):
                if any(keyword.lower() in procurement.get('description', '').lower() for keyword in [title, skill, experience, keyword, challenge]):
                    match = True

            if match:
                results.append(f"Title: {procurement.get('title', 'Unknown')}\nDescription: {procurement.get('description', 'No description available')}")

        return results



class ActionListServices(Action):
    def name(self) -> Text:
        return "action_list_services"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Extract service titles from PROCUREMENTS JSON
        services = [procurement.get('title', 'No service title listed') for procurement in PROCUREMENTS]
        services_text = "\n".join(services)
        dispatcher.utter_message(text=f"Our services include:\n{services_text}")
        return []


class ActionListProcurements(Action):
    def name(self) -> Text:
        return "action_list_procurements"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Extract procurement titles from PROCUREMENTS JSON
        procurements = [procurement.get('title', 'No procurement title listed') for procurement in PROCUREMENTS]
        procurements_text = "\n".join(procurements)
        dispatcher.utter_message(text=f"Our procurements include:\n{procurements_text}")
        return []


class ActionListExpertise(Action):
    def name(self) -> Text:
        return "action_list_expertise"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Extract expertise areas from PROCUREMENTS JSON
        expertise = set()  # Use a set to avoid duplicates
        for procurement in PROCUREMENTS:
            expertise.update(procurement.get('skills', []))
        expertise_text = "\n".join(expertise)
        dispatcher.utter_message(text=f"Our areas of expertise include:\n{expertise_text}")
        return []


class ActionListKeywords(Action):
    def name(self) -> Text:
        return "action_list_keywords"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Extract keywords from PROCUREMENTS JSON
        keywords = set()  # Use a set to avoid duplicates
        for procurement in PROCUREMENTS:
            keywords.update(procurement.get('keywords', []))
        keywords_text = "\n".join(keywords)
        dispatcher.utter_message(text=f"Some keywords related to our services are:\n{keywords_text}")
        return []


class ActionListIndustry(Action):
    def name(self) -> Text:
        return "action_list_industry"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Extract industries from PROCUREMENTS JSON
        industries = set()  # Use a set to avoid duplicates
        for procurement in PROCUREMENTS:
            industries.update(procurement.get('industry', []))
        industries_text = "\n".join(industries)
        dispatcher.utter_message(text=f"We operate in the following industries:\n{industries_text}")
        return []


class ActionListSector(Action):
    def name(self) -> Text:
        return "action_list_sector"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Extract sectors from PROCUREMENTS JSON
        sectors = set()  # Use a set to avoid duplicates
        for procurement in PROCUREMENTS:
            sectors.update(procurement.get('sector', []))
        sectors_text = "\n".join(sectors)
        dispatcher.utter_message(text=f"We are active in the following sectors:\n{sectors_text}")
        return []


class ActionListChallenges(Action):
    def name(self) -> Text:
        return "action_list_challenges"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Extract challenges from PROCUREMENTS JSON
        challenges = set()  # Use a set to avoid duplicates
        for procurement in PROCUREMENTS:
            challenges.update(procurement.get('challenges_addressed', []))
        challenges_text = "\n".join(challenges)
        dispatcher.utter_message(text=f"We address the following challenges:\n{challenges_text}")
        return []


class ActionListDescription(Action):
    def name(self) -> Text:
        return "action_list_description"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Extract descriptions from PROCUREMENTS JSON
        descriptions = [procurement.get('description', 'No description available') for procurement in PROCUREMENTS]
        descriptions_text = "\n\n".join(descriptions)
        dispatcher.utter_message(text=f"Here is a description of our procurements:\n{descriptions_text}")
        return []


class ActionListExperience(Action):
    def name(self) -> Text:
        return "action_list_experience"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Collect all unique experiences from PROCUREMENTS
        experiences = set()
        for procurement in PROCUREMENTS:
            experiences.update(procurement['experience'])
        
        # Format response
        response = "Here are the experiences listed across procurements:\n" + "\n".join(experiences)
        dispatcher.utter_message(text=response)
        return []


class ActionListAll(Action):
    def name(self) -> Text:
        return "action_list_all"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Provide a summary of all procurements
        response = ""
        for procurement in PROCUREMENTS:
            response += f"**Title:** {procurement['title']}\n" \
                        f"**Skills:** {', '.join(procurement['skills'])}\n" \
                        f"**Experience:** {', '.join(procurement['experience'])}\n" \
                        f"**Keywords:** {', '.join(procurement['keywords'])}\n" \
                        f"**Industry:** {', '.join(procurement['industry'])}\n" \
                        f"**Sector:** {', '.join(procurement['sector'])}\n" \
                        f"**Challenges Addressed:** {', '.join(procurement['challenges_addressed'])}\n" \
                        f"**Description:** {procurement['description']}\n\n"
        
        dispatcher.utter_message(text="Here is the comprehensive list of all procurements:\n" + response)
        return []


class ActionProvideInformation(Action):
    def name(self) -> str:
        return "action_provide_information"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict) -> list:
        # Load the CSV file with procurement details
        df = pd.read_csv('./data_file.csv')
        
        # Get the latest user message and extract the title entity
        user_message = tracker.latest_message.get('text')
        title_entity = next(tracker.get_latest_entity_values("title"), None)

        if title_entity:
            # Perform a case-insensitive search in the Title column for the provided title
            matching_procurement = df[df['Title'].str.contains(title_entity, case=False, na=False)]
            
            if not matching_procurement.empty:
                # Retrieve the 'Experience & Benefits delivered' column for the matched title
                experience_details = matching_procurement.iloc[0]['Experience & Benefits delivered']
                
                # Respond with the corresponding procurement details
                response = f"Details for '{title_entity}':\n{experience_details}"
                dispatcher.utter_message(response)
            else:
                dispatcher.utter_message(f"I couldn't find any procurements with the title '{title_entity}'.")
        else:
            dispatcher.utter_message("Please provide a valid procurement title.")

        return []