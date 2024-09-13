from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from difflib import get_close_matches
import logging
from rasa_sdk.types import DomainDict
import pandas as pd
from fuzzywuzzy import process
from rasa_sdk.events import SlotSet
import random


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
    {
        "title": "Major Application Upgrades and Procurement",
        "skills": ["Application Upgrades", "Procurement", "Cost Optimization"],
        "experience": ["Improved license terms", "Cost profile enhancement", "Future-proofing business requirements"],
        "keywords": ["Application Upgrades", "Procurement", "Cost Optimization"],
        "industry": ["Private Sector"],
        "sector": ["Various"],
        "challenges_addressed": ["Application replacement procurement", "License term improvements"],
        "description": "Conducted major application upgrades and replacement procurement across various private sector organizations, resulting in enhanced license terms, improved cost profiles, and future-proofing of business requirements."
    },
    {
        "title": "End-to-End Supply Operations Review",
        "skills": ["Supply Chain Management", "Logistics Review", "Transformational Change"],
        "experience": ["Reviewed supply logistics model", "Senior roles in retail distribution and manufacturing"],
        "keywords": ["Supply Chain", "Logistics", "Transformational Change"],
        "industry": ["Manufacturing"],
        "sector": ["Retail", "Manufacturing"],
        "challenges_addressed": ["Supply logistics optimization", "Transformational change management"],
        "description": "Currently leading a comprehensive review of the supply logistics model for a manufacturing company, with previous experience in senior roles in retail distribution and manufacturing."
    },
    {
        "title": "IT Procurement Advisory",
        "skills": ["IT Procurement", "Negotiation", "Cost Savings"],
        "experience": ["Microsoft Enterprise Agreement renewal", "Audit settlement", "Franchise renegotiations", "Website rebuild", "Ecommerce and PIM system sourcing"],
        "keywords": ["IT Procurement", "Negotiation", "Cost Savings"],
        "industry": ["IT"],
        "sector": ["Private"],
        "challenges_addressed": ["Global agreement negotiations", "Audit cost reduction", "Contract renegotiations", "Website redevelopment"],
        "description": "Led IT procurement advisory including global Microsoft Enterprise Agreement negotiations, audit settlements, franchise contract renegotiations, website rebuilds, and sourcing of new ecommerce and PIM systems."
    },
    {
        "title": "Alignment of IT Agreements with TSA",
        "skills": ["IT Agreements", "Contract Compliance", "TSA Management"],
        "experience": ["Reviewed IT contracts for TSB", "Ensured compliance with Transfer Services Agreement"],
        "keywords": ["IT Agreements", "TSA", "Contract Compliance"],
        "industry": ["Financial Services"],
        "sector": ["Banking"],
        "challenges_addressed": ["Contractual compliance", "IT agreement alignment with TSA"],
        "description": "Supported the alignment of IT agreements with Transfer Services Agreements (TSA) for TSB, ensuring that IT contracts met the contractual commitments between parties and with suppliers."
    },
    {
        "title": "Setting Up and Running an SRM Model in a Greenfield Environment",
        "skills": ["Supplier Relationship Management", "Governance Structure", "Supplier Performance"],
        "experience": ["Established SRM model for Tesco", "Implemented consistent governance and performance reporting"],
        "keywords": ["Supplier Relationship Management", "Governance", "Performance Reporting"],
        "industry": ["Retail"],
        "sector": ["Goods Not for Resale"],
        "challenges_addressed": ["Supplier management", "Governance structure implementation", "Performance reporting"],
        "description": "Set up an SRM model for Tesco's Goods Not for Resale division, focusing on consistent supplier management, performance reporting, and governance structure in a Greenfield environment."
    },
    {
        "title": "Microsoft Enterprise Agreement Renewal",
        "skills": ["Contract Renewal", "Licensing Optimization", "Negotiation"],
        "experience": ["Microsoft contract renewals", "Optimal licensing outcomes"],
        "keywords": ["Microsoft", "Contract Renewal", "Licensing"],
        "industry": ["IT"],
        "sector": ["Private", "Public"],
        "challenges_addressed": ["Timely contract renewals", "Licensing optimization"],
        "description": "Managed Microsoft Enterprise Agreement renewals across various sectors, ensuring timely contract renewals with the best licensing outcomes."
    },
    {
        "title": "Cybersecurity Transformation Procurement",
        "skills": ["Cybersecurity Procurement", "Cost Savings", "RFP Management"],
        "experience": ["Led procurement with $37M budget", "Achieved 40% cost savings", "Managed 32 RFPs"],
        "keywords": ["Cybersecurity", "Procurement", "Cost Savings"],
        "industry": ["Cybersecurity"],
        "sector": ["Various"],
        "challenges_addressed": ["Cybersecurity procurement", "Cost reduction", "RFP management"],
        "description": "Led cybersecurity procurement for Natura Co. with a $37M budget, achieving a 40% cost saving and managing 32 RFPs to enhance organizational cybersecurity."
    },
    {
        "title": "ERP Systems Procurement",
        "skills": ["ERP Implementation", "Vendor Negotiation", "Contract Management"],
        "experience": ["ERP system implementation at Brunel University", "Managed $20M PeopleSoft implementation", "Negotiated deals with Oracle and Infosys"],
        "keywords": ["ERP Systems", "Implementation", "Vendor Negotiation"],
        "industry": ["Education", "Private Sector"],
        "sector": ["Higher Education", "Corporate"],
        "challenges_addressed": ["ERP system selection", "Vendor negotiation", "Contract management"],
        "description": "Led ERP system implementations for Brunel University and Hays, including significant deals with Oracle and Infosys, managing contracts and overseeing major agreements."
    },
    {
        "title": "Strategic Software Licenses Procurement",
        "skills": ["Software Licensing", "Negotiation", "Cost Savings"],
        "experience": ["Secured competitive pricing", "Created global deal pipelines", "Achieved over $45M in savings"],
        "keywords": ["Software Licensing", "Negotiation", "Cost Savings"],
        "industry": ["IT"],
        "sector": ["Various"],
        "challenges_addressed": ["Competitive pricing", "Global deal management", "Savings achievement"],
        "description": "Negotiated competitive pricing and managed global deal pipelines for software licenses, achieving significant savings and efficient contract signoffs."
    },
    {
        "title": "Procurement Support for Strategic Transformation Programmes",
        "skills": ["Transformation Programmes", "Procurement Management", "Savings Achievement"],
        "experience": ["Managed software license integration", "Secured $2M in savings", "Oversaw $15B IT spend"],
        "keywords": ["Transformation", "Procurement", "Savings"],
        "industry": ["Various"],
        "sector": ["Global"],
        "challenges_addressed": ["Software license integration", "Procurement for large-scale projects", "Savings achievement"],
        "description": "Provided procurement support for strategic transformation programmes, including software license integration, securing significant savings, and managing substantial IT spend across global projects."
    },
    {
        "title": "Public Sector IT Reseller Model",
        "skills": ["Reseller Model Creation", "Process Streamlining", "Cost Reduction"],
        "experience": ["Streamlined buying practices", "Delivered additional savings"],
        "keywords": ["Public Sector", "Reseller Model", "Process Improvement"],
        "industry": ["Public Sector", "IT"],
        "sector": ["Public"],
        "challenges_addressed": ["Streamlining procurement processes", "Reducing risk", "Delivering savings"],
        "description": "Created a preferred reseller model for a large public sector organization to streamline processes and reduce risk while delivering additional savings."
    },
    {
        "title": "Expert Support on Public Sector Procurement Process",
        "skills": ["Procurement Projects", "Compliance", "Governance Review"],
        "experience": ["Delivered procurement projects across various sectors", "Ensured compliance with public sector legislation", "Led webinars for tender response and procurement governance"],
        "keywords": ["Procurement", "Compliance", "Public Sector", "Governance"],
        "industry": ["Public Sector", "Healthcare", "Education"],
        "sector": ["Public"],
        "challenges_addressed": ["Ensuring compliance", "Procurement governance review", "Understanding tender requirements"],
        "description": "Delivered a wide range of procurement projects and ensured compliance with public sector legislation. Provided governance reviews and training on procurement processes."
    },
    {
        "title": "Expert Procurement Support for Compliance with Public Contracts Regulations",
        "skills": ["Procurement Documentation", "Business Case Development", "Compliance Training"],
        "experience": ["Audited and updated procurement documentation", "Developed business cases with HM Treasury", "Delivered compliance training for teams"],
        "keywords": ["Procurement Compliance", "Public Contracts Regulations", "Business Case"],
        "industry": ["Public Sector", "Healthcare"],
        "sector": ["Public"],
        "challenges_addressed": ["Compliance with regulations", "Business case approval", "Procurement governance"],
        "description": "Provided expert procurement support to ensure compliance with Public Contracts Regulations and updated procurement documentation. Developed business cases and delivered training on procurement governance."
    },
    {
        "title": "Procurement Strategy for Management Consultancies",
        "skills": ["Procurement Strategy", "Cost Avoidance", "Supplier Negotiation"],
        "experience": ["Delivered significant cost avoidance for global banks", "Led global transformation programs", "Completed market research for supply chain optimization"],
        "keywords": ["Procurement Strategy", "Consultancy", "Cost Avoidance", "Supplier Management"],
        "industry": ["Finance", "Consultancy", "FMCG"],
        "sector": ["Private"],
        "challenges_addressed": ["Cost avoidance", "Supplier negotiation", "Transformation program leadership"],
        "description": "Developed procurement strategies for management consultancies, achieving significant cost avoidance and leading global transformation programs. Conducted market research for optimizing supply chain processes."
    },
    {
        "title": "Procurement of Employee Rewards Programs",
        "skills": ["Employee Rewards", "Flexible Benefits", "Global Sourcing"],
        "experience": ["Implemented flexible benefits platform for UK bank", "Led global sourcing project for BioScience organization", "Established vendor management governance"],
        "keywords": ["Employee Rewards", "Flexible Benefits", "Global Sourcing"],
        "industry": ["Finance", "BioScience"],
        "sector": ["Private"],
        "challenges_addressed": ["Implementing flexible benefits", "Global employee assistance program", "Vendor management"],
        "description": "Negotiated and implemented employee rewards programs, including flexible benefits platforms and global employee assistance programs. Established new governance structures and achieved significant savings."
    },
    {
        "title": "Fleet Procurement and Green Fleet/Decarbonisation Delivery",
        "skills": ["Fleet Management", "CO2 Emissions Reduction", "Cost Savings"],
        "experience": ["Delivered fleet transformation strategy", "Reduced CO2 emissions and achieved cost savings", "Renegotiated with suppliers and streamlined resources"],
        "keywords": ["Fleet Management", "Green Fleet", "Cost Savings"],
        "industry": ["Facilities Management"],
        "sector": ["Private"],
        "challenges_addressed": ["Fleet transformation", "Emissions reduction", "Cost savings"],
        "description": "Developed and delivered a fleet transformation strategy, reducing CO2 emissions and achieving significant cost savings. Streamlined supplier management and focused on electric vehicle use."
    },
    {
        "title": "Legal Services Procurement",
        "skills": ["Legal Services Procurement", "Sourcing Strategy", "Cost Reduction"],
        "experience": ["Led transformation program for legal services", "Achieved significant cost reductions", "Implemented new panel structures"],
        "keywords": ["Legal Services", "Procurement", "Cost Reduction"],
        "industry": ["Legal"],
        "sector": ["Private"],
        "challenges_addressed": ["Reducing legal services costs", "Implementing new sourcing strategies", "Streamlining panel structures"],
        "description": "Led a transformation program for legal services procurement, achieving cost reductions and implementing new panel structures. Delivered significant annualized savings and improved legal service processes."
    },
    {
        "title": "Strategic Contingent Workforce Procurement",
        "skills": ["Contingent Workforce Management", "MSP Implementation", "Cost Management"],
        "experience": ["Implemented hybrid MSP recruitment solution", "Managed global contingent labor sourcing strategy", "Achieved cost savings through MSP solutions"],
        "keywords": ["Contingent Workforce", "MSP", "Cost Management"],
        "industry": ["BioScience", "Aerospace Defense"],
        "sector": ["Private"],
        "challenges_addressed": ["Contingent workforce management", "MSP implementation", "Cost savings"],
        "description": "Implemented strategic contingent workforce procurement solutions, managing global sourcing strategies and achieving significant cost savings through MSP solutions."
    },
    {
        "title": "Procurement support for Business Process Outsourcing (BPO)",
        "skills": ["BPO Procurement", "Contract Negotiation", "Transformation Management"],
        "experience": ["Renegotiated BPO contracts for healthcare provider", "Led global payroll transformation", "Managed outsourced maintenance contracts"],
        "keywords": ["BPO", "Contract Negotiation", "Transformation"],
        "industry": ["Healthcare", "Technology"],
        "sector": ["Private"],
        "challenges_addressed": ["BPO contract renegotiation", "Payroll transformation", "Outsourced maintenance management"],
        "description": "Provided procurement support for BPO, renegotiating contracts, leading global payroll transformations, and managing outsourced maintenance contracts."
    },
    {
        "title": "Procurement of Clinical Research Services",
        "skills": ["Clinical Research Procurement", "Contract Negotiation", "Cost Savings"],
        "experience": ["Negotiated cost savings for clinical trials", "Reviewed and updated research contracts", "Mitigated contractual and regulatory risks"],
        "keywords": ["Clinical Research", "Procurement", "Cost Savings"],
        "industry": ["Pharmaceuticals"],
        "sector": ["Private"],
        "challenges_addressed": ["Cost savings in clinical trials", "Contract compliance", "Risk mitigation"],
        "description": "Led procurement for clinical research services, achieving cost savings and updating contracts to comply with standards. Managed risks and ensured compliance."
    },
    {
        "title": "Engineering & Technical Services Procurement - Aircraft Engine Maintenance",
        "skills": ["Engine Maintenance Procurement", "Contract Management", "Cost Savings"],
        "experience": ["Managed engine maintenance contracts", "Implemented JIT leased engine strategy", "Negotiated and managed support equipment contracts"],
        "keywords": ["Engine Maintenance", "Contract Management", "Cost Savings"],
        "industry": ["Aerospace"],
        "sector": ["Private"],
        "challenges_addressed": ["Engine maintenance management", "Cost savings", "Contract negotiation"],
        "description": "Managed long-term engine maintenance contracts, implemented JIT leased engine strategies, and negotiated support equipment contracts for a global airline."
    },
    {
        "title": "Procurement support for IT/ITO/xPO Outsourcing",
        "skills": ["IT Outsourcing", "Contract Finalization", "Cost Avoidance"],
        "experience": ["Avoided costs on IT infrastructure integration", "Established new IT contractual suite", "Negotiated outsourcing contracts"],
        "keywords": ["IT Outsourcing", "Contract Management", "Cost Avoidance"],
        "industry": ["Technology", "Automotive"],
        "sector": ["Private"],
        "challenges_addressed": ["IT outsourcing", "Contract finalization", "Cost avoidance"],
        "description": "Supported IT outsourcing initiatives, finalizing contracts and negotiating terms. Achieved cost avoidance and established new contractual frameworks."
    },
    {
        "title": "Optimising Corporate Travel Management",
        "skills": ["Travel Management", "Contract Negotiation", "Policy Review"],
        "experience": ["Developed travel management strategy", "Negotiated travel and MICE rates", "Reviewed corporate travel policy post-COVID"],
        "keywords": ["Travel Management", "Contract Negotiation", "Policy Review"],
        "industry": ["Travel", "Facilities Management"],
        "sector": ["Private"],
        "challenges_addressed": ["Travel management optimization", "Rate negotiations", "Policy review"],
        "description": "Optimized corporate travel management, negotiated rates, and reviewed policies to deliver cost savings and efficiencies while maintaining service quality."
    },
    {
        "title": "ESG Programmes in Procurement",
        "skills": ["ESG Implementation", "Supplier Management", "Contractual Clauses"],
        "experience": ["Implemented ESG programs with Tier 1 suppliers", "Introduced ESG clauses into contracts"],
        "keywords": ["ESG", "Supplier Management", "Contractual Clauses"],
        "industry": ["Various"],
        "sector": ["Private"],
        "challenges_addressed": ["ESG program implementation", "Supplier engagement", "Contractual compliance"],
        "description": "Implemented ESG programs and integrated ESG clauses into contracts, engaging with suppliers to ensure compliance and improve sustainability practices."
    },
    {
        "title": "Procurement Management of Corporate Travel Policy",
        "skills": ["Travel Management", "Stakeholder Engagement", "Policy Writing", "Negotiation"],
        "experience": ["Managed domestic and corporate travel programs", "Negotiated rates with hotels, airlines, and taxi services", "Worked with C-suite and other stakeholders"],
        "keywords": ["Travel Management", "Negotiation", "Cost Savings"],
        "industry": ["Insurance"],
        "sector": ["Private"],
        "challenges_addressed": ["Cost savings", "Service quality", "Risk management"],
        "description": "Managed a domestic and corporate travel program for a major UK-based FS insurance company, negotiating rates with suppliers and rewriting the Travel Policy, which led to significant cost savings and service quality improvements."
    },
    {
        "title": "Managing High-Value Public Sector Contracts in Procurement",
        "skills": ["Contract Management", "Supplier Performance", "Risk Management"],
        "experience": ["Managed high-value PPP and PFI contracts", "Improved supplier performance", "Streamlined governance models"],
        "keywords": ["Public Sector", "Supplier Management", "Governance"],
        "industry": ["Public Sector"],
        "sector": ["Public"],
        "challenges_addressed": ["Supplier performance", "Contractual complexity", "Risk mitigation"],
        "description": "Managed high-value public sector contracts with London Underground, focusing on improving supplier performance and risk management, implementing streamlined governance models, and enhancing collaboration."
    },
    {
        "title": "Implementation of a Contract Lifecycle Management Solution (e.g., Apttus)",
        "skills": ["Contract Lifecycle Management", "Compliance Tracking", "Dashboard Reporting"],
        "experience": ["Implemented Apttus CLM solution", "Updated and managed contract information", "Increased compliance scores"],
        "keywords": ["Contract Management", "Compliance", "Dashboard"],
        "industry": ["Various"],
        "sector": ["Private"],
        "challenges_addressed": ["Contract compliance", "Process optimization", "Data management"],
        "description": "Implemented Apttus CLM solution across multiple organizations, improving contract compliance and process management through updated tracking and dashboard reporting."
    },
    {
        "title": "Software Licensing when Setting Up a New Company or Corporate Entity",
        "skills": ["Software Licensing", "Supplier Selection", "Cost Management"],
        "experience": ["Led software licensing process for new insurance business", "Reduced future costs significantly"],
        "keywords": ["Licensing", "Cost Reduction", "Implementation"],
        "industry": ["Insurance"],
        "sector": ["Private"],
        "challenges_addressed": ["Cost management", "Supplier selection", "Implementation efficiency"],
        "description": "Oversaw the software licensing process for a new insurance business, achieving significant cost reductions through strategic licensing agreements and efficient implementation."
    },
    {
        "title": "How to Perform IT Contract Reviews",
        "skills": ["Contract Review", "Negotiation", "Supplier Management"],
        "experience": ["Performed numerous IT contract reviews", "Negotiated and amended terms", "Managed supplier replacements"],
        "keywords": ["Contract Review", "Negotiation", "Supplier Management"],
        "industry": ["Various"],
        "sector": ["Private"],
        "challenges_addressed": ["Contract terms", "Cost reduction", "Supplier management"],
        "description": "Conducted IT contract reviews to improve business processes, negotiating terms, and managing supplier relationships to reduce costs and improve terms."
    },
    {
        "title": "Contract Drafting & Negotiation for IT Outsourced Services",
        "skills": ["Contract Drafting", "Negotiation", "Document Management"],
        "experience": ["Drafted and negotiated IT outsourcing agreements", "Managed document versions and storage"],
        "keywords": ["Contract Drafting", "Negotiation", "Outsourcing"],
        "industry": ["Insurance", "IT Services"],
        "sector": ["Private"],
        "challenges_addressed": ["Document management", "Contract negotiation", "Service delivery"],
        "description": "Drafted and negotiated IT outsourcing contracts, managing document versions and negotiations to ensure favorable terms and service delivery."
    },
    {
        "title": "Contracts Novation (Acquisition & Exit Planning) - Outsourced Services",
        "skills": ["Contract Novation", "Acquisition Planning", "Exit Planning"],
        "experience": ["Managed contract novation for various acquisitions and exits", "Reviewed terms and requirements"],
        "keywords": ["Contract Novation", "Acquisition", "Exit Planning"],
        "industry": ["Various"],
        "sector": ["Private"],
        "challenges_addressed": ["Contract transitions", "Term review", "Business requirements"],
        "description": "Managed the novation of contracts during acquisitions and exits, reviewing and updating terms to meet business needs and ensure smooth transitions."
    },
    {
        "title": "Strategic Sourcing for Food, Pharma, Leisure, Retail & Telecoms Industries",
        "skills": ["Strategic Sourcing", "Supply Chain Improvement", "Cost Savings"],
        "experience": ["Delivered cost savings and supply chain improvements", "Led strategic sourcing programs across multiple sectors"],
        "keywords": ["Strategic Sourcing", "Cost Savings", "Supply Chain"],
        "industry": ["Food", "Pharma", "Leisure", "Retail", "Telecoms"],
        "sector": ["Private"],
        "challenges_addressed": ["Cost savings", "Supply chain optimization", "Sector-specific challenges"],
        "description": "Provided strategic sourcing and supply chain optimization across various high-value sectors, achieving significant cost savings and improvements."
    },
    {
        "title": "Advice on Procurement Transformation and Outsourcing",
        "skills": ["Procurement Transformation", "Outsourcing", "Cost Savings"],
        "experience": ["Led procurement transformations for blue-chip clients", "Managed outsourcing projects across sectors"],
        "keywords": ["Procurement Transformation", "Outsourcing", "Cost Savings"],
        "industry": ["Various"],
        "sector": ["Private"],
        "challenges_addressed": ["Transformation management", "Outsourcing challenges", "Cost savings"],
        "description": "Provided expert advice on procurement transformations and outsourcing projects, delivering cost savings and operational efficiencies across various sectors."
    },
    {
        "title": "Insight on Sustainable Procurement and ESG Integration",
        "skills": ["Sustainable Procurement", "ESG Integration", "Ethical Sourcing"],
        "experience": ["Developed sustainable procurement practices", "Promoted ethical sourcing and fair trade"],
        "keywords": ["Sustainable Procurement", "ESG", "Ethical Sourcing"],
        "industry": ["Various"],
        "sector": ["Private"],
        "challenges_addressed": ["Sustainability", "Ethical sourcing", "ESG criteria"],
        "description": "Developed and executed sustainable procurement practices that align with corporate sustainability goals, enhancing ESG criteria and promoting ethical sourcing."
    },
    {
        "title": "Advice on Complex Contract and Supplier Management Issues",
        "skills": ["Contract Management", "Supplier Negotiations", "Cost Reduction"],
        "experience": ["Managed complex contracts and supplier negotiations", "Delivered savings and value enhancements"],
        "keywords": ["Contract Management", "Supplier Negotiations", "Cost Reduction"],
        "industry": ["Various"],
        "sector": ["Private"],
        "challenges_addressed": ["Complex contracts", "Supplier negotiations", "Cost savings"],
        "description": "Advised on complex contract and supplier management issues, delivering significant savings and enhancing value through effective negotiations and contract management."
    },
    {
        "title": "IT Digital Transformation incl Cloud, Enterprise software & CyberSecurity",
        "skills": ["Digital Transformation", "Cloud Services", "Cybersecurity"],
        "experience": ["Led IT digital transformation initiatives", "Managed multimillion-pound contracts for IT services"],
        "keywords": ["Digital Transformation", "Cloud Services", "Cybersecurity"],
        "industry": ["Various"],
        "sector": ["Private"],
        "challenges_addressed": ["Digital transformation", "Cloud services", "Cybersecurity"],
        "description": "Led IT digital transformation projects, managing significant contracts for IT services, cloud solutions, and cybersecurity to support broader digital transformation efforts."
    },
    {
        "title": "Guidance to Drive Global Supply Chain Optimisation for CPG and Pharma",
        "skills": ["Supply Chain Optimization", "Strategic Sourcing", "Global Sourcing"],
        "experience": ["Optimized global supply chains for CPG and pharma sectors", "Delivered substantial savings through strategic sourcing"],
        "keywords": ["Supply Chain Optimization", "Strategic Sourcing", "Global Sourcing"],
        "industry": ["CPG", "Pharma"],
        "sector": ["Private"],
        "challenges_addressed": ["Supply chain optimization", "Cost savings", "Global sourcing"],
        "description": "Provided guidance on global supply chain optimization for CPG and pharma sectors, delivering significant savings and improving supply chain resilience."
    },
    {
        "title": "Insight on Risk Management for Outsourcing and BPO",
        "skills": ["Risk Management", "Outsourcing", "BPO"],
        "experience": ["Led risk management for outsourcing arrangements", "Ensured compliance and operational integrity"],
        "keywords": ["Risk Management", "Outsourcing", "BPO"],
        "industry": ["Various"],
        "sector": ["Private"],
        "challenges_addressed": ["Risk management", "Compliance", "Operational integrity"],
        "description": "Provided insights on risk management for outsourcing and BPO arrangements, focusing on compliance and operational integrity to reduce exposure and enhance resilience."
    },
    {
        "title": "Guidance on Enhancing your Procurement Operating Model",
        "skills": ["Procurement Transformation", "Operating Model Enhancement", "Change Management"],
        "experience": ["Led procurement transformations and enhanced operating models", "Managed diverse procurement teams"],
        "keywords": ["Procurement Transformation", "Operating Model", "Change Management"],
        "industry": ["Various"],
        "sector": ["Private"],
        "challenges_addressed": ["Procurement transformation", "Operating model enhancement", "Change management"],
        "description": "Guided organizations in enhancing their procurement operating models, managing transformations and change across policy, process, and technology domains."
    },
    {
        "title": "Global Hotel Rate Negotiations via e-Auction",
        "skills": ["e-Auction", "Rate Negotiation", "Cost Savings"],
        "experience": ["Ran e-Auctions for global hotel rates", "Achieved significant savings"],
        "keywords": ["e-Auction", "Rate Negotiation", "Cost Savings"],
        "industry": ["Travel"],
        "sector": ["Private"],
        "challenges_addressed": ["Cost savings", "Rate negotiation", "Efficiency"],
        "description": "Conducted over 20 e-Auctions for hotel properties, achieving a 20% reduction in annual hotel spend for a major client."
    },
    {
        "title": "Business Process Outsourcing Strategy",
        "skills": ["Outsourcing", "Payroll Services", "Managed Legal Service", "Cost Savings"],
        "experience": [
            "Oversaw a £30M payroll outsourcing contract, one of the largest in the UK, covering 110,000 employees",
            "Set up an Outsourced Managed Legal Service for LSEG, saving over £400K",
            "Sourced Big 4 support for Internal Audit, saving £180K",
            "Renewed MSP contract, resulting in £3.8M in cost savings"
        ],
        "keywords": ["Payroll Outsourcing", "Managed Legal Service", "Cost Efficiency"],
        "industry": ["Financial Services", "Travel"],
        "sector": ["Private"],
        "challenges_addressed": ["Cost savings", "Efficiency", "Vendor management"],
        "description": "Directed major outsourcing deals and managed services for payroll and legal functions, achieving significant cost savings and efficiency improvements."
    },
    {
        "title": "IT Outsourcing for Application Development and Support",
        "skills": ["IT Outsourcing", "Commercial Negotiations", "Cost Savings"],
        "experience": [
            "Managed £350M offshore ITO spend at Lloyds Banking Group, saving £50M and consolidating suppliers",
            "Repositioned TCS as a strategic provider for LSEG, achieving 35M in cost savings",
            "Negotiated in-house hiring of PSCs, leading to cost savings and IR35 risk mitigation"
        ],
        "keywords": ["IT Outsourcing", "Cost Savings", "IR35"],
        "industry": ["Financial Services"],
        "sector": ["Private"],
        "challenges_addressed": ["Cost savings", "Supplier consolidation", "IR35 compliance"],
        "description": "Led major IT outsourcing contracts and negotiations, achieving substantial cost savings and strategic supplier positioning."
    },
    {
        "title": "Negotiating with Top Tier Consulting and Professional Services Suppliers",
        "skills": ["Consulting Negotiations", "Cost Synergies", "Framework Agreements"],
        "experience": [
            "Achieved £15M cost savings through new commercial structures with Big 4 firms",
            "Saved £950K through new commercial framework with Clifford Chance",
            "Negotiated fixed price SoW with Freshfields, reducing costs by £15M"
        ],
        "keywords": ["Consulting", "Cost Savings", "Commercial Framework"],
        "industry": ["Professional Services"],
        "sector": ["Private"],
        "challenges_addressed": ["Cost savings", "Commercial structuring", "Contract negotiations"],
        "description": "Negotiated high-value consulting and professional services contracts, delivering significant cost savings and strategic benefits."
    },
    {
        "title": "Managed Services Strategy for HR, Legal, and Finance",
        "skills": ["Managed Services", "Contract Renewals", "Cost Efficiency"],
        "experience": [
            "Established outsourced managed legal service for LSEG, saving £400K",
            "Renewed MSP agreement, achieving £3.8M in cost savings",
            "Sourced and renewed various finance and HR managed services"
        ],
        "keywords": ["Managed Services", "Cost Savings", "Vendor Management"],
        "industry": ["Financial Services"],
        "sector": ["Private"],
        "challenges_addressed": ["Cost savings", "Service management", "Vendor alignment"],
        "description": "Developed and managed outsourced services for HR, legal, and finance functions, driving cost savings and operational efficiency."
    },
    {
        "title": "ERP Systems Integrator Selection",
        "skills": ["ERP Systems", "Vendor Selection", "Cost Avoidance"],
        "experience": [
            "Led the selection of an ERP Systems Integrator for Oracle Financials, saving £1.1M",
            "Managed vendor negotiations and contract details"
        ],
        "keywords": ["ERP Systems", "Vendor Selection", "Cost Avoidance"],
        "industry": ["Various"],
        "sector": ["Private"],
        "challenges_addressed": ["Vendor selection", "Cost management"],
        "description": "Directed the selection process for ERP systems integration, achieving significant cost avoidance and project efficiency."
    },
    {
        "title": "Launching and Scaling a Procurement Function",
        "skills": ["Procurement Strategy", "Team Scaling", "Policy Development"],
        "experience": [
            "Scaled procurement function from 8 to 80 FTEs and £250M to £4BN spend",
            "Developed procurement policies and processes to support business growth"
        ],
        "keywords": ["Procurement Function", "Team Development", "Policy Creation"],
        "industry": ["Financial Services"],
        "sector": ["Private"],
        "challenges_addressed": ["Team scaling", "Policy development", "Business growth"],
        "description": "Led the creation and scaling of a procurement function, supporting significant business growth and operational efficiency."
    },
    {
        "title": "Creating a Unified Global Procurement Function",
        "skills": ["Global Procurement", "Organizational Transformation", "Client Alignment"],
        "experience": [
            "Unified three regional teams into a global procurement function at Randstad",
            "Improved client alignment and internal processes, resulting in best-in-class team feedback"
        ],
        "keywords": ["Global Procurement", "Organizational Transformation", "Client Alignment"],
        "industry": ["HR Solutions"],
        "sector": ["Private"],
        "challenges_addressed": ["Team integration", "Client satisfaction", "Operational efficiency"],
        "description": "Successfully integrated and transformed global procurement teams, enhancing client alignment and operational performance."
    },
    {
        "title": "Comprehensive Workforce Management Strategy",
        "skills": ["Workforce Management", "Strategic Planning", "Talent Services"],
        "experience": [
            "Developed a holistic workforce management strategy at LSEG",
            "Created a new team and strategy for IT Outsourcing and contingent labour, resulting in significant cost savings"
        ],
        "keywords": ["Workforce Management", "Strategic Planning", "Cost Savings"],
        "industry": ["Financial Services"],
        "sector": ["Private"],
        "challenges_addressed": ["Workforce strategy", "Cost management", "Talent services"],
        "description": "Implemented a comprehensive workforce management strategy, driving efficiency and cost savings across talent services and resourcing."
    },
    {
        "title": "Procurement Leadership in Mergers & Acquisitions",
        "skills": ["Mergers & Acquisitions", "Procurement Transformation", "Integration Planning"],
        "experience": [
            "Led procurement for Refinitiv acquisition, delivering £28M in cost savings",
            "Developed integration plans and vendor strategies to support merger activities"
        ],
        "keywords": ["Mergers & Acquisitions", "Procurement Transformation", "Integration Planning"],
        "industry": ["Financial Services"],
        "sector": ["Private"],
        "challenges_addressed": ["M&A integration", "Cost savings", "Vendor management"],
        "description": "Directed procurement and integration strategies for major mergers and acquisitions, achieving significant cost savings and operational success."
    },
    {
        "title": "Managing IR35 & Global Compliance within Contingent Labour",
        "skills": ["IR35 Compliance", "Global Compliance", "Cost Savings"],
        "experience": [
            "Expert in IR35 compliance, delivering multimillion-pound savings",
            "Redrafted IR35 policies and educated teams on compliance"
        ],
        "keywords": ["IR35 Compliance", "Global Compliance", "Cost Savings"],
        "industry": ["Various"],
        "sector": ["Private"],
        "challenges_addressed": ["Compliance management", "Cost savings", "Policy development"],
        "description": "Managed IR35 compliance and global regulations, achieving significant cost savings and ensuring policy adherence."
    },
    {
        "title": "Sourcing Cloud and Hybrid Hosting & Storage Solutions",
        "skills": ["Cloud Solutions", "Hybrid Hosting", "Procurement Strategy"],
        "experience": [
            "Led strategic procurement for a £150M cloud and hybrid hosting project",
            "Developed and executed procurement strategies for migration and transformation services"
        ],
        "keywords": ["Cloud Solutions", "Hybrid Hosting", "Procurement Strategy"],
        "industry": ["Government"],
        "sector": ["Public"],
        "challenges_addressed": ["Cloud migration", "Transformation services", "Procurement strategy"],
        "description": "Directed the procurement of cloud and hybrid hosting solutions, delivering a successful transformation project for a government department."
    },
    {
        "title": "Procuring Cyber Security Solutions",
        "skills": ["Cyber Security", "Procurement", "Managed Services"],
        "experience": [
            "Procured cyber security services and products, including managed services",
            "Delivered value for money solutions for government departments and educational institutions"
        ],
        "keywords": ["Cyber Security", "Procurement", "Managed Services"],
        "industry": ["Government", "Education"],
        "sector": ["Public"],
        "challenges_addressed": ["Cyber security", "Value for money", "Service procurement"],
        "description": "Managed procurement of cyber security solutions, achieving value for money and effective service delivery for various public sector clients."
    },
    {
        "title": "Sourcing of IT Service Desk and ITSM Tooling",
        "skills": ["IT Service Desk", "ITSM Tooling", "Contract Management"],
        "experience": [
            "Managed contracts for IT Service Desk and ITSM tooling",
            "Handled extensions, new procurements, and reprocurements, integrating with cyber security and end-user compute services"
        ],
        "keywords": ["IT Service Desk", "ITSM Tooling", "Contract Management"],
        "industry": ["Government"],
        "sector": ["Public"],
        "challenges_addressed": ["Service management", "Tool integration", "Contract handling"],
        "description": "Directed procurement for IT service desk and ITSM tooling, ensuring effective service management and integration with broader IT services."
    },
    {
        "title": "Procurement Strategy for Data Migration and Management (SharePoint)",
        "skills": ["Data Migration", "SharePoint Solutions", "Security Standards"],
        "experience": [
            "Successfully delivered data migration and SharePoint solutions with high security standards in a transformational environment"
        ],
        "keywords": ["Data Migration", "SharePoint", "Security Standards"],
        "industry": ["Technology"],
        "sector": ["Private"],
        "challenges_addressed": ["Data migration", "Security", "Transformation"],
        "description": "Led the procurement and implementation of data migration and SharePoint solutions, ensuring compliance with high-level security standards."
    },
    {
        "title": "Software Procurement, Divestment, and Renewals Management",
        "skills": ["Software Procurement", "Renewals Management", "Category Management"],
        "experience": [
            "Managed high volume annual renewals of business-critical software, achieving savings of over £14M in 18 months",
            "Streamlined software licensing to enable forward-looking and remove duplication"
        ],
        "keywords": ["Software Procurement", "Renewals", "Cost Savings"],
        "industry": ["Various"],
        "sector": ["Private"],
        "challenges_addressed": ["Cost savings", "License management", "Efficiency"],
        "description": "Oversaw procurement, divestment, and renewals for business-critical software, achieving significant savings and improving licensing management."
    },
    {
        "title": "Expert Creation of Excel-based Tasks/Skills Matrix for Procurement",
        "skills": ["Skills Matrix", "Cross-Training", "Task Distribution"],
        "experience": [
            "Developed tasks/skills matrix for multiple clients, improving cross-training, identifying skills shortages, and enhancing task distribution",
            "Created training plans to address skills gaps and streamline onboarding"
        ],
        "keywords": ["Skills Matrix", "Cross-Training", "Task Distribution"],
        "industry": ["Various"],
        "sector": ["Private"],
        "challenges_addressed": ["Skill gaps", "Training", "Onboarding"],
        "description": "Designed and implemented Excel-based skills matrices, driving cross-training, identifying skill shortages, and improving departmental efficiency."
    },
    {
        "title": "Creation of Excel-based Supplier Assessment Form for Procurement",
        "skills": ["Supplier Assessment", "Performance Measurement", "Supplier Collaboration"],
        "experience": [
            "Developed supplier assessment forms leading to improved supplier communications and performance",
            "Facilitated better internal marketing for procurement through accurate performance measurement"
        ],
        "keywords": ["Supplier Assessment", "Performance Measurement", "Collaboration"],
        "industry": ["Various"],
        "sector": ["Private"],
        "challenges_addressed": ["Supplier performance", "Collaboration", "Internal marketing"],
        "description": "Created supplier assessment forms that enhanced collaboration, performance measurement, and internal visibility, improving supplier management."
    },
    {
        "title": "Development of Procurement Target Operating Models",
        "skills": ["Procurement Target Operating Models", "Strategic Planning", "Operational Efficiency"],
        "experience": [
            "Developed and implemented procurement target operating models in various roles, including SVP Supply Chain Procurement at The Marketing Store and Director of Procurement Centre of Excellence at Arm Ltd"
        ],
        "keywords": ["Procurement Models", "Strategic Planning", "Operational Efficiency"],
        "industry": ["Various"],
        "sector": ["Private"],
        "challenges_addressed": ["Operational efficiency", "Strategic planning"],
        "description": "Designed and executed target operating models for procurement, enhancing operational efficiency and strategic alignment across organizations."
    },
    {
        "title": "Procurement Support for MSP and VMS Selection for Contingent Workforce",
        "skills": ["MSP Selection", "VMS Selection", "Contingent Workforce Management"],
        "experience": [
            "Provided procurement support for Managed Service Providers (MSP) and Vendor Management Systems (VMS) selection for contingent workforce management"
        ],
        "keywords": ["MSP", "VMS", "Contingent Workforce"],
        "industry": ["Various"],
        "sector": ["Private"],
        "challenges_addressed": ["Contingent workforce management", "Vendor selection"],
        "description": "Supported the selection process for MSP and VMS to manage contingent workforce needs effectively, optimizing procurement outcomes."
    },
    {
        "title": "Marketing Procurement Support for Digital Solutions",
        "skills": ["Marketing Procurement", "Digital Solutions", "Project Management"],
        "experience": [
            "Provided interim project management support for digital solutions procurement at Paragon Customer Communications",
            "Supported marketing procurement strategies at Smith & Nephew Plc"
        ],
        "keywords": ["Marketing Procurement", "Digital Solutions", "Project Management"],
        "industry": ["Marketing"],
        "sector": ["Private"],
        "challenges_addressed": ["Procurement support", "Digital solutions"],
        "description": "Delivered marketing procurement support for digital solutions, including project management and strategic sourcing."
    },
    {
        "title": "Automotive Cost Reduction Strategy",
        "skills": ["Cost Reduction", "Automotive Sector", "Technical Cost Management"],
        "experience": [
            "Delivered over 10% savings in the first year across major automotive clients, including Nissan and VW/Audi Group",
            "Expertise in technical and commercial cost reduction within direct commodity groups"
        ],
        "keywords": ["Cost Reduction", "Automotive", "Technical Management"],
        "industry": ["Automotive"],
        "sector": ["Private"],
        "challenges_addressed": ["Cost reduction", "Technical management"],
        "description": "Implemented cost reduction strategies in the automotive sector, achieving significant savings and optimizing technical cost management."
    },
    {
        "title": "Electronics Manufacturing Cost Optimisation",
        "skills": ["Cost Optimisation", "Electronics Manufacturing", "Strategic Planning"],
        "experience": [
            "Achieved significant cost savings in electronics manufacturing across defense and automotive sectors, including work with Nissan and McLaren",
            "Expertise in strategic and tactical cost reduction"
        ],
        "keywords": ["Cost Optimisation", "Electronics Manufacturing", "Strategic Planning"],
        "industry": ["Electronics"],
        "sector": ["Private"],
        "challenges_addressed": ["Cost optimisation", "Manufacturing efficiency"],
        "description": "Led cost optimisation initiatives in electronics manufacturing, delivering substantial savings through strategic and tactical planning."
    },
    {
        "title": "Marine and Cargo Handling Solutions Cost Optimisation",
        "skills": ["Cost Optimisation", "Marine Sector", "Cargo Handling"],
        "experience": [
            "Achieved 15% cost savings in marine and cargo handling solutions with Cargotec, MacGregor, and Hiab"
        ],
        "keywords": ["Cost Optimisation", "Marine Sector", "Cargo Handling"],
        "industry": ["Marine"],
        "sector": ["Private"],
        "challenges_addressed": ["Cost reduction", "Marine sector efficiency"],
        "description": "Optimized cost in marine and cargo handling solutions, achieving significant savings and enhancing operational efficiency."
    },
    {
        "title": "Cost Reduction for Complex Technical Commodities",
        "skills": ["Cost Reduction", "Technical Commodities", "Strategic Sourcing"],
        "experience": [
            "Delivered significant savings across diverse technical commodities with top manufacturers"
        ],
        "keywords": ["Cost Reduction", "Technical Commodities", "Sourcing"],
        "industry": ["Various"],
        "sector": ["Private"],
        "challenges_addressed": ["Cost reduction", "Technical sourcing"],
        "description": "Drove cost reduction in complex technical commodities, achieving notable savings through strategic sourcing and management."
    },
    {
        "title": "Delivering Cost Efficiency in Highly Regulated Industries",
        "skills": ["Cost Efficiency", "Regulated Industries", "Compliance"],
        "experience": [
            "Specialized in cost efficiency and compliance in defense, automotive, and marine sectors, delivering savings while meeting regulatory standards"
        ],
        "keywords": ["Cost Efficiency", "Regulated Industries", "Compliance"],
        "industry": ["Defense", "Automotive", "Marine"],
        "sector": ["Private"],
        "challenges_addressed": ["Cost efficiency", "Regulatory compliance"],
        "description": "Focused on achieving cost efficiency in highly regulated industries, ensuring compliance while delivering significant savings."
    },
    {
        "title": "Optimising Internal Combustion Engine Manufacturing Costs",
        "skills": ["Cost Optimisation", "Engine Manufacturing", "Strategic Management"],
        "experience": [
            "Achieved significant cost savings in internal combustion engine manufacturing with Perkins, Cummins, and Stellantis"
        ],
        "keywords": ["Cost Optimisation", "Engine Manufacturing", "Strategic Management"],
        "industry": ["Automotive"],
        "sector": ["Private"],
        "challenges_addressed": ["Cost reduction", "Manufacturing efficiency"],
        "description": "Optimized manufacturing costs for internal combustion engines, delivering notable savings through strategic management."
    },
    {
        "title": "Defence Sector Cost Reduction and Sourcing Strategy",
        "skills": ["Cost Reduction", "Defence Sector", "Sourcing Strategy"],
        "experience": [
            "Specialized in cost reduction and sourcing strategy within the defense sector, including nuclear and electronics"
        ],
        "keywords": ["Cost Reduction", "Defence Sector", "Sourcing Strategy"],
        "industry": ["Defense"],
        "sector": ["Private"],
        "challenges_addressed": ["Cost reduction", "Sourcing strategy"],
        "description": "Implemented cost reduction and sourcing strategies in the defense sector, focusing on nuclear and electronics for optimal results."
    },
    {
        "title": "Outsourced Managed Services - Post Contract Management",
        "skills": ["Post Contract Management", "SLA Monitoring", "Vendor Management"],
        "experience": [
            "Managed post-contract services for various clients, including Aviva Insurance and European Bank, overseeing SLA obligations and commercial issues"
        ],
        "keywords": ["Post Contract Management", "SLA Monitoring", "Vendor Management"],
        "industry": ["Insurance", "Banking"],
        "sector": ["Private"],
        "challenges_addressed": ["SLA management", "Commercial issue resolution"],
        "description": "Handled post-contract management for outsourced services, including SLA monitoring and resolution of commercial issues."
    },
    {
        "title": "Best Practices for Dispute Resolution in Commercial Contracts",
        "skills": ["Dispute Resolution", "Commercial Contracts", "Negotiation"],
        "experience": [
            "Managed and resolved commercial disputes for various clients, including securing settlements and negotiating contract terms effectively"
        ],
        "keywords": ["Dispute Resolution", "Commercial Contracts", "Negotiation"],
        "industry": ["Various"],
        "sector": ["Private"],
        "challenges_addressed": ["Dispute resolution", "Negotiation"],
        "description": "Applied best practices for dispute resolution in commercial contracts, achieving favorable outcomes through effective negotiation and management."
    },
    {
        "title": "Procurement of Building Maintenance and Repair Services",
        "skills": ["Vendor Management", "Building Maintenance", "Repair Services"],
        "experience": [
            "Built a vendor of record shortlist for building maintenance and repair services, implementing VMI programs for cost reduction and improved cash flow"
        ],
        "keywords": ["Vendor Management", "Building Maintenance", "Repair Services"],
        "industry": ["Construction"],
        "sector": ["Private"],
        "challenges_addressed": ["Vendor selection", "Cost reduction"],
        "description": "Developed procurement strategies for building maintenance and repair services, optimizing vendor management and cost efficiency."
    },
    {
        "title": "Security Services and Systems Procurement",
        "skills": ["Security Systems Design", "Regulatory Compliance", "Tendering"],
        "experience": [
            "Designed and installed a security system with 120 cameras during a factory refurbishment, meeting stringent regulatory requirements for the pharma sector.",
            "Worked with multiple clients to understand security staff needs, scoped works, and tendered requirements, achieving cost savings while ensuring supplier capability."
        ],
        "keywords": ["Security Systems", "Regulatory Compliance", "Tendering"],
        "industry": ["Pharma"],
        "sector": ["Private"],
        "challenges_addressed": ["Compliance with strict regulations", "Cost-saving through effective tendering"],
        "description": "Oversaw the design and installation of a comprehensive security system for a factory, ensuring all requirements were met while achieving significant cost savings through effective tendering."
    },
    {
        "title": "Cleaning and Sanitation Services Procurement",
        "skills": ["Cleaning Procedures", "Tender Management", "KPI Monitoring"],
        "experience": [
            "Updated cleaning procedures in a pharma manufacturing facility to enhance cleanliness.",
            "Managed 10 tenders for cleaning services, developed scopes of work, and ensured winning bidders met quality and cost criteria.",
            "Monitored supplier performance against agreed KPIs."
        ],
        "keywords": ["Cleaning Services", "Tender Management", "KPI Monitoring"],
        "industry": ["Pharma"],
        "sector": ["Private"],
        "challenges_addressed": ["Improving cleanliness", "Managing cost and quality through tendering"],
        "description": "Enhanced cleaning procedures and managed the tender process for cleaning services, ensuring high standards of cleanliness and cost efficiency."
    },
    {
        "title": "Waste Management and Recycling Programs Procurement",
        "skills": ["Waste Management", "Framework Agreements", "Circular Waste Management"],
        "experience": [
            "Established framework agreements for waste management services across public sector organizations, including diverse waste types.",
            "Supported circular waste management initiatives to keep recyclable waste within the UK.",
            "Developed agreements for waste management in the UK and Canada, ensuring robust recycling systems."
        ],
        "keywords": ["Waste Management", "Recycling", "Circular Economy"],
        "industry": ["Public Sector"],
        "sector": ["Public"],
        "challenges_addressed": ["Waste management efficiency", "Promoting recycling within the UK"],
        "description": "Developed comprehensive waste management agreements and supported circular waste management initiatives, ensuring effective recycling and cost management."
    },
    {
        "title": "Landscaping and Grounds Maintenance Procurement",
        "skills": ["Landscaping", "Grounds Maintenance", "Tendering"],
        "experience": [
            "Tendered landscaping services for public sector clients managing historic sites, selecting a single supplier to ensure consistency and cost savings.",
            "Managed landscaping requirements for parks and gardens, agreeing on specifications and selecting suppliers."
        ],
        "keywords": ["Landscaping", "Grounds Maintenance", "Tendering"],
        "industry": ["Public Sector"],
        "sector": ["Public"],
        "challenges_addressed": ["Cost savings", "Maintaining consistency across multiple sites"],
        "description": "Managed landscaping tenders and supplier selection for various public sector clients, ensuring high-quality services and significant cost savings."
    },
    {
        "title": "R&D Services Procurement for Innovation",
        "skills": ["R&D Services", "Innovation", "Technology Procurement"],
        "experience": [
            "Procured specialized R&D equipment for the renewables sector, including hexapods for wave analysis and simulators for lidar units."
        ],
        "keywords": ["R&D Services", "Innovation", "Technology Procurement"],
        "industry": ["Renewables"],
        "sector": ["Private"],
        "challenges_addressed": ["Supporting innovative R&D projects with specialized equipment"],
        "description": "Procured advanced R&D equipment to support innovation in the renewables sector, ensuring timely acquisition of cutting-edge technology."
    },
    {
        "title": "Procurement of Scientific and Laboratory Equipment",
        "skills": ["Laboratory Equipment", "Facility Retrofit", "Supply Chain Management"],
        "experience": [
            "Supported the retrofitting of a facility for cannabis production by sourcing high-tech lab equipment and managing shipment and inventory.",
            "Set up consignment stock contracts to ensure continuous supply and improve cash flow."
        ],
        "keywords": ["Laboratory Equipment", "Facility Retrofit", "Supply Chain Management"],
        "industry": ["Pharma"],
        "sector": ["Private"],
        "challenges_addressed": ["Timely procurement", "Supply chain optimization"],
        "description": "Managed the procurement of laboratory equipment for a facility retrofit, ensuring timely delivery and continuous supply through consignment stock contracts."
    },
    {
        "title": "Health and Safety Equipment and Services Procurement",
        "skills": ["Safety Equipment", "Vendor Management", "Cost Reduction"],
        "experience": [
            "Implemented safety measures for a large limestone quarry, including installing reverse cameras and sirens on 400 vehicles.",
            "Negotiated safety equipment revisions for a pharma client, including testing and evaluating various products."
        ],
        "keywords": ["Safety Equipment", "Vendor Management", "Cost Reduction"],
        "industry": ["Quarrying", "Pharma"],
        "sector": ["Private"],
        "challenges_addressed": ["Ensuring safety", "Cost-effective procurement"],
        "description": "Oversaw the procurement of safety equipment for diverse industries, negotiating contracts to reduce costs and ensure continuous supply."
    },
    {
        "title": "Real Estate and Lease Management Services Procurement",
        "skills": ["Lease Negotiation", "Property Management", "Real Estate Strategy"],
        "experience": [
            "Researched and negotiated lease terms for office properties, managed subleasing to mitigate costs and risks."
        ],
        "keywords": ["Lease Negotiation", "Property Management", "Real Estate Strategy"],
        "industry": ["Various"],
        "sector": ["Private"],
        "challenges_addressed": ["Lease negotiation", "Cost and risk management"],
        "description": "Researched and negotiated lease terms, managed subleasing strategies to cover costs and reduce risks associated with property management."
    },
    {
        "title": "Spend Analysis and Cost Reduction Strategies",
        "skills": ["Cost Analysis", "Data Management", "KPI Reviews"],
        "experience": [
            "Set up cost-saving reports and procedures for accurate cost saving reporting throughout procurement teams.",
            "Conducted deep dives into equipment spare parts usage to optimize maintenance approaches and reduce costs."
        ],
        "keywords": ["Cost Analysis", "Data Management", "KPI Reviews"],
        "industry": ["Various"],
        "sector": ["Private"],
        "challenges_addressed": ["Cost reduction", "Optimizing maintenance approaches"],
        "description": "Developed and implemented strategies for cost savings and efficiency, including detailed analysis of spare parts usage and procurement practices."
    },
    {
        "title": "Change Management in Procurement",
        "skills": ["Process Mapping", "KPI Development", "Contractual Alignment"],
        "experience": [
            "Aligned business objectives with process mapping, developed and managed KPIs, and reviewed contractual agreements to drive change."
        ],
        "keywords": ["Change Management", "Process Mapping", "KPI Development"],
        "industry": ["Various"],
        "sector": ["Private"],
        "challenges_addressed": ["Aligning objectives with processes", "Managing change effectively"],
        "description": "Led change management initiatives in procurement, focusing on aligning processes with business objectives and managing KPIs and contractual agreements."
    },
    {
        "title": "Third-Party Logistics (3PL) Services Procurement",
        "skills": ["3PL Management", "KPI Development", "Cost Reduction"],
        "experience": [
            "Acted as Interim General Manager for a 3PL provider, developed KPIs, and achieved significant cost savings through stock recycling and reuse.",
            "Renegotiated 3PL provision for Bosch Rexroth, integrating WMS with SAP and managing non-moving stock efficiently."
        ],
        "keywords": ["3PL Management", "KPI Development", "Cost Reduction"],
        "industry": ["Various"],
        "sector": ["Private"],
        "challenges_addressed": ["Cost savings", "Integration and efficiency"],
        "description": "Managed 3PL services, developed KPIs, and achieved cost savings through efficient stock management and integration with client systems."
    },
    {
        "title": "Packaging Solutions and Materials Procurement",
        "skills": ["Packaging Design", "Cost Negotiation", "Sustainability"],
        "experience": [
            "Developed innovative packaging solutions for motor parts to prevent rust and damage during shipping.",
            "Negotiated cost and criteria for recyclable packaging alternatives with DS Smith."
        ],
        "keywords": ["Packaging Design", "Cost Negotiation", "Sustainability"],
        "industry": ["Manufacturing"],
        "sector": ["Private"],
        "challenges_addressed": ["Protective packaging", "Cost and sustainability"],
        "description": "Created effective packaging solutions to protect products during shipping and negotiated cost-effective, sustainable alternatives."
    },
    {
        "title": "Supply Chain Risk Management Advisory",
        "skills": ["Risk Identification", "Mitigation Strategies", "Crisis Management"],
        "experience": [
            "Supported clients in identifying and mitigating supply chain risks, including just-in-time issues and supplier recovery planning.",
            "Developed and implemented risk management frameworks and crisis recovery plans."
        ],
        "keywords": ["Risk Management", "Crisis Management", "Mitigation Strategies"],
        "industry": ["Various"],
        "sector": ["Private"],
        "challenges_addressed": ["Supply chain risk", "Crisis management"],
        "description": "Advised clients on managing supply chain risks, including developing strategies for crisis recovery and risk mitigation."
    },
    {
        "title": "Managing Supply Chain Efficiency and Performance",
        "skills": ["Supply Chain Training", "Continuous Improvement", "Lean Approaches", "Data Management", "KPI Reviews"],
        "experience": [
            "Carried out supply chain training for MBA students on behalf of the Supply Chain Academy.",
            "Worked with Bosch Rexroth to evaluate inefficiencies and identify opportunities for continuous improvement in their global supply chain.",
            "Provided best practice insights into retail operations for Boots, focusing on bridging the gap between overarching strategy and day-to-day tasks through lean approaches and automation."
        ],
        "keywords": ["Supply Chain Efficiency", "Continuous Improvement", "Lean Approaches"],
        "industry": ["Manufacturing", "Retail"],
        "sector": ["Private"],
        "challenges_addressed": ["Operational inefficiencies", "Disconnect between strategy and daily operations"],
        "description": "Enhanced supply chain efficiency by implementing lean approaches, training, and continuous improvement strategies, ensuring alignment between strategy and day-to-day operations."
    },
    {
        "title": "Reverse Logistics and Returns Management Strategies",
        "skills": ["Reverse Logistics", "Sustainability", "Data Analytics", "Process Mapping"],
        "experience": [
            "Worked with Amazon on global reverse logistics operations and Boots on their Goods Not For Retail (GNFR) operation, focusing on recycling, reuse, and reducing carbon footprint.",
            "Developed strategies for making reverse logistics processes leaner and more efficient, leveraging data and analytics to optimize solutions."
        ],
        "keywords": ["Reverse Logistics", "Sustainability", "Data Analytics"],
        "industry": ["Retail"],
        "sector": ["Private"],
        "challenges_addressed": ["Sustainability in reverse logistics", "Optimization of returns processes"],
        "description": "Implemented reverse logistics strategies to enhance sustainability and process efficiency, focusing on recycling, reuse, and leveraging data for improved solutions."
    },
    {
        "title": "Enhancing Supply Chain Transparency and Traceability",
        "skills": ["Supply Chain Transparency", "Warehouse Management", "Carbon Footprint Tracking", "System Integration"],
        "experience": [
            "Created standard work in documentation and transparency exercises for Bosch.",
            "Developed a bespoke iOS-based warehouse management system for Boots, integrating with existing systems while maintaining IT governance.",
            "Built a carbon footprint tracker for Goods Not For Retail (GNFR) items and investigated planning transparency systems for poultry FMCG suppliers."
        ],
        "keywords": ["Supply Chain Transparency", "Warehouse Management", "Carbon Footprint Tracking"],
        "industry": ["Retail"],
        "sector": ["Private"],
        "challenges_addressed": ["Documentation and transparency", "System integration and carbon footprint tracking"],
        "description": "Enhanced supply chain transparency and traceability through the development of documentation standards, warehouse management systems, and carbon footprint tracking solutions."
    },
    {
        "title": "Software License Asset Compliance Management",
        "skills": ["Software License Management", "Compliance", "Data Consolidation"],
        "experience": [
            "Provided an overview of software license usage and compliance for a European bank.",
            "Consolidated software license data for Survitec Ltd, creating dashboards for utilization and renewal tracking.",
            "Supported tracking of hardware and software asset information for Computer Sciences Corporation."
        ],
        "keywords": ["Software License Management", "Compliance", "Data Consolidation"],
        "industry": ["Banking", "Technology"],
        "sector": ["Private"],
        "challenges_addressed": ["Software license compliance", "Data consolidation and utilization tracking"],
        "description": "Managed software license compliance by consolidating data, tracking utilization, and ensuring adherence to renewal and termination policies."
    },
    {
        "title": "Effective Strategic Procurement Transformation",
        "skills": ["Procurement Transformation", "Shared Services", "P2P Processes", "Operating Model Development"],
        "experience": [
            "Transformed procurement departments in various organizations, including setting up shared service departments and implementing new procurement operating models.",
            "Delivered P2P transformation projects and developed procurement business partnering strategies."
        ],
        "keywords": ["Procurement Transformation", "Shared Services", "P2P Processes"],
        "industry": ["Various"],
        "sector": ["Private"],
        "challenges_addressed": ["Procurement inefficiencies", "Implementation of new models and processes"],
        "description": "Led strategic procurement transformations by setting up shared services, developing new operating models, and implementing P2P processes to drive efficiency and effectiveness."
    },
    {
        "title": "How to Develop a Long-Term Procurement Strategy",
        "skills": ["Procurement Strategy", "Organizational Analysis", "Operating Models", "Value for Money"],
        "experience": [
            "Implemented long-term procurement strategies in roles at JnJ, Greensquare, APCOA, and EBIT.",
            "Conducted organizational analysis to identify gaps, redefine operating models, and evaluate options for delivering value for money."
        ],
        "keywords": ["Procurement Strategy", "Organizational Analysis", "Value for Money"],
        "industry": ["Various"],
        "sector": ["Private"],
        "challenges_addressed": ["Developing effective long-term strategies", "Aligning procurement function with organizational objectives"],
        "description": "Developed and implemented long-term procurement strategies by analyzing current support structures, identifying gaps, and creating efficient operating models to deliver value for money."
    },
    {
        "title": "Effective Change Management in Procurement",
        "skills": ["Change Management", "Stakeholder Engagement", "Process Improvement"],
        "experience": [
            "Led change management initiatives within procurement functions for various UK high street retailers.",
            "Facilitated change acceptance, identified opportunities, and guided teams through challenging conversations to drive improvement."
        ],
        "keywords": ["Change Management", "Stakeholder Engagement", "Process Improvement"],
        "industry": ["Retail"],
        "sector": ["Private"],
        "challenges_addressed": ["Managing change effectively", "Driving process improvements"],
        "description": "Directed change management efforts in procurement functions, focusing on stakeholder engagement, process improvement, and guiding teams through change acceptance and implementation."
    },
    {
        "title": "P2P Transformation & Optimisation",
        "skills": ["P2P Systems", "Workflow Optimization", "Implementation"],
        "experience": [
            "Guided P2P transformation projects, including the setup and implementation of Ariba in a £500m business.",
            "Worked with various P2P systems like InTend, Proactis, and Coupa to optimize workflows and approval processes."
        ],
        "keywords": ["P2P Systems", "Workflow Optimization", "Implementation"],
        "industry": ["Various"],
        "sector": ["Private"],
        "challenges_addressed": ["System optimization", "Workflow and approval process management"],
        "description": "Optimized P2P systems by setting up and implementing solutions, improving workflows, and managing approval processes to enhance overall efficiency."
    },
    {
        "title": "Building a Shared Service Centre for P2P",
        "skills": ["Shared Services", "P2P Management", "Benefit Analysis"],
        "experience": [
            "Implemented shared service centres for various organizations, reviewing business needs and assessing the benefits of the shared service model in the P2P environment."
        ],
        "keywords": ["Shared Services", "P2P Management", "Benefit Analysis"],
        "industry": ["Various"],
        "sector": ["Private"],
        "challenges_addressed": ["Implementing shared services", "Driving P2P benefits"],
        "description": "Built shared service centres by analyzing business needs and assessing the benefits of shared service models in the P2P environment."
    },
    {
        "title": "Embedding SRM Best Practice in Procurement",
        "skills": ["Supplier Relationship Management", "Performance Improvement", "Provider Exit Management"],
        "experience": [
            "Delivered SRM development programs for underperforming providers, managed provider exits, and worked on improving performance and service delivery."
        ],
        "keywords": ["Supplier Relationship Management", "Performance Improvement", "Provider Exit Management"],
        "industry": ["Various"],
        "sector": ["Private"],
        "challenges_addressed": ["Improving provider performance", "Managing provider exits"],
        "description": "Implemented SRM best practices to enhance provider performance, manage exits, and improve service delivery."
    },
    {
        "title": "Compliance Policies & Process for OJEU",
        "skills": ["Compliance", "Regulatory Requirements", "Policy Development"],
        "experience": [
            "Reviewed and updated compliance policies and procedures for a housing association, ensuring adherence to OJEU regulations and involving the compliance department in the process."
        ],
        "keywords": ["Compliance", "Regulatory Requirements", "Policy Development"],
        "industry": ["Public Sector"],
        "sector": ["Public"],
        "challenges_addressed": ["Adherence to regulatory requirements", "Policy development and implementation"],
        "description": "Developed and implemented compliance policies and processes to ensure adherence to OJEU regulations and other regulatory requirements."
    },
    {
        "title": "Best Practice for Category Management & Stakeholder Engagement",
        "skills": ["Category Management", "Stakeholder Engagement", "Process Review"],
        "experience": [
            "Reviewed and analyzed category management processes, providing fresh perspectives and finding additional value through effective stakeholder engagement and spend segmentation."
        ],
        "keywords": ["Category Management", "Stakeholder Engagement", "Process Review"],
        "industry": ["Various"],
        "sector": ["Private"],
        "challenges_addressed": ["Optimizing category management", "Effective stakeholder engagement"],
        "description": "Enhanced category management practices by reviewing processes, segmenting spend, and engaging stakeholders to drive additional value."
    },
    {
        "title": "Corporate Travel Management Procurement",
        "skills": ["Travel Management", "Cost Savings", "Centralized Travel Policy"],
        "experience": [
            "Analyzed travel management companies to source suitable suppliers, achieving cost benefits through centralized travel policies and leveraging deals on hotels, rail, and air travel."
        ],
        "keywords": ["Travel Management", "Cost Savings", "Centralized Policy"],
        "industry": ["Corporate Travel"],
        "sector": ["Private"],
        "challenges_addressed": ["Cost reduction in travel management", "Centralizing travel policies"],
        "description": "Optimized corporate travel management by implementing centralized policies, achieving cost savings, and leveraging travel deals."
    },
    {
        "title": "Corporate Fleet Management Strategies",
        "skills": ["Fleet Management", "Cost Savings", "Policy Development"],
        "experience": [
            "Worked with global and UK fleet management companies to deliver cost savings through lease reviews, policy changes, and consolidation, achieving significant operational benefits."
        ],
        "keywords": ["Fleet Management", "Cost Savings", "Policy Development"],
        "industry": ["Fleet Management"],
        "sector": ["Private"],
        "challenges_addressed": ["Cost reduction in fleet management", "Policy and operational improvements"],
        "description": "Implemented fleet management strategies to achieve cost savings and operational benefits through policy changes, lease reviews, and consolidation."
    },
    {
        "title": "Fuel Audits and Management Optimisation",
        "skills": ["Fuel Management", "Cost Reduction", "Fraud Prevention"],
        "experience": [
            "Delivered fuel management solutions to improve transparency and auditing, resulting in a cost reduction and elimination of fraudulent fuel usage."
        ],
        "keywords": ["Fuel Management", "Cost Reduction", "Fraud Prevention"],
        "industry": ["Fuel Management"],
        "sector": ["Private"],
        "challenges_addressed": ["Improving fuel management transparency", "Preventing fuel misuse"],
        "description": "Enhanced fuel management through improved transparency, auditing, and fraud prevention, resulting in significant cost reductions."
    },
    {
        "title": "Catering and Hospitality Procurement Solutions",
        "skills": ["Catering Procurement", "Hospitality Services", "Supplier Management"],
        "experience": [
            "Provided innovative catering and hospitality solutions, working with both small and large suppliers to tailor services to business needs."
        ],
        "keywords": ["Catering Procurement", "Hospitality Services", "Supplier Management"],
        "industry": ["Catering", "Hospitality"],
        "sector": ["Private"],
        "challenges_addressed": ["Tailoring catering solutions", "Supplier management"],
        "description": "Developed and delivered catering and hospitality solutions, sourcing from various suppliers to meet business needs effectively."
    },
    {
        "title": "Employee Wellness & Leisure Services Procurement",
        "skills": ["Wellness Services", "Leisure Services", "Employee Benefits"],
        "experience": [
            "Delivered a range of leisure and wellness services, including on-site gym and swimming facilities, exercise classes, and other employee benefits tailored to business needs."
        ],
        "keywords": ["Wellness Services", "Leisure Services", "Employee Benefits"],
        "industry": ["Wellness", "Leisure"],
        "sector": ["Private"],
        "challenges_addressed": ["Providing tailored wellness services", "Managing employee benefits"],
        "description": "Implemented employee wellness and leisure services, including facilities and classes, to enhance employee benefits and satisfaction."
    },
]


# When user ask all covered industries
class ActionAskIndustriesCovered(Action):
    def name(self) -> Text:
        return "action_ask_industries_covered"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict) -> List[Dict[Text, Any]]:
        # Extract unique industries
        industries = set()
        for procurement in PROCUREMENTS:
            industries.update(procurement.get("industry", []))
        
        # Convert to a list and sort it for a neat response
        industries_list = sorted(industries)
        
        # Create a friendly message
        if industries_list:
            industries_message = ", ".join(industries_list)
            dispatcher.utter_message(text=f"We proudly cover a wide range of industries including: {industries_message}.")
        else:
            dispatcher.utter_message(text="I'm currently updating our information on industries covered. Please check back later.")
        
        return []        

# When user ask about procurements in specific industry
class ActionAskIndustrySpecific(Action):
    def name(self) -> Text:
        return "actions_ask_industry_specific"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict) -> list:
        industry_slot = tracker.get_slot("industry")
        
        # Convert PROCUREMENTS list to DataFrame
        df = pd.DataFrame(PROCUREMENTS)
        
        # If no industry slot value, return a message
        if not industry_slot:
            dispatcher.utter_message(text="Sorry, I am currently learning about different industries. Please provide a specific industry.")
            # Show all procurements
            if not df.empty:
                response = "\n".join(f"Title: {row['title']}\nDescription: {row['description']}" for index, row in df.iterrows())
                dispatcher.utter_message(text=f"Here are some procurements: \n{response}")
            return [SlotSet("industry", None)]

        # Fuzzy matching to find the closest industry names in the data
        industries = df['industry'].explode().unique()
        best_match, score = process.extractOne(industry_slot, industries)
        
        # Filter procurements based on the matched industry
        filtered_df = df[df['industry'].apply(lambda x: best_match in x)]

        if filtered_df.empty:
            dispatcher.utter_message(text=f"Sorry, I couldn't find any procurements right now, please check back later.")
        else:
            response = "\n".join(f"Title: {row['title']}\nDescription: {row['description']}" for index, row in filtered_df.iterrows())
            dispatcher.utter_message(text=f"Here are the procurements in the '{best_match}' industry: \n{response}")
        
        return [SlotSet("industry", None)]

# When user ask all covered sectors
class ActionListSectors(Action):

    def name(self) -> Text:
        return "action_ask_sectors_covered"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Extract sectors from the PROCUREMENTS list
        sectors = set()
        for procurement in PROCUREMENTS:
            sectors.update(procurement["sector"])

        # Prepare a user-friendly response
        if sectors:
            sectors_list = ", ".join(sectors)
            message = f"We cover the following sectors: {sectors_list}. Is there anything specific you would like to know more about?"
        else:
            message = "I’m currently learning about the sectors we cover. Can you please try again later?"

        dispatcher.utter_message(text=message)
        return []

# When user ask about procurements in specific sector
class ActionListProcurementsBySector(Action):

    def name(self) -> Text:
        return "action_ask_procurements_by_sector"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Get the sector entity from the tracker
        sector = tracker.get_slot('sector')

        print(f"Sector: {sector}")

        # Filter procurements by sector
        procurements = [p for p in PROCUREMENTS if sector in p["sector"]]

        # Prepare a user-friendly response
        if procurements:
            messages = [f"Here are some procurements in the {sector} sector:"]
            for procurement in procurements:
                messages.append(f"- {procurement['title']}: {procurement['description']}")
            message = "\n".join(messages)
        else:
            if sector:
                message = f"Sorry, I couldn't find any procurements in the {sector} sector. Please try a different sector or check back later."
            else:
                message = "I’m currently gathering more information. Can you please specify the sector you are interested in?"

        dispatcher.utter_message(text=message)
        return [SlotSet("sector", None)]

# When user ask about procurements by providing sector and industry both
class ActionAskProcurementsByIndustryAndSector(Action):
    def name(self) -> Text:
        return "action_ask_procurements_by_industry_and_sector"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Extract slots
        industry = tracker.get_slot('industry')
        sector = tracker.get_slot('sector')
        
        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(PROCUREMENTS)
        
        
        if industry and sector:
            filtered_df = df[(df['industry'].apply(lambda x: industry in x)) & (df['sector'].apply(lambda x: sector in x))]
        elif industry:
            filtered_df = df[df['industry'].apply(lambda x: industry in x)]
        elif sector:
            filtered_df = df[df['sector'].apply(lambda x: sector in x)]
        else:
            filtered_df = df
        
        if not filtered_df.empty:
            response = f"I found the following procurements for industry '{industry}' and sector '{sector}':\n"
            for _, row in filtered_df.iterrows():
                response += f"- **{row['title']}**: {row['description']}\n"
        else:
            if industry and sector:
                response = f"Sorry, I couldn't find any procurements for industry '{industry}' and sector '{sector}'. I’m still learning more about this."
            elif industry:
                response = f"Sorry, I couldn't find any procurements in the industry '{industry}'. I’m still learning more about this."
            elif sector:
                response = f"Sorry, I couldn't find any procurements in the sector '{sector}'. I’m still learning more about this."
            else:
                response = "Sorry, I couldn’t find any procurements. Please try specifying industry or sector."

        dispatcher.utter_message(text=response)
        return []

# When user ask procuremtn by title, keywords, skill etc..
class ActionSearchByTitle(Action):

    def name(self) -> str:
        return "action_ask_procurement_search_by_title"

    def run(self, dispatcher: CollectingDispatcher, tracker, domain):
        title = tracker.get_slot('title')

        if title:
            # Create a pandas DataFrame from the PROCUREMENTS list
            df = pd.DataFrame(PROCUREMENTS)

            # Combine all relevant fields into a single string per procurement for fuzzy matching
            df['combined'] = df.apply(lambda row: ' '.join(str(value) for value in [
                row['title'], ' '.join(row['skills']), ' '.join(row['experience']),
                ' '.join(row['keywords']), row['description'], ' '.join(row['challenges_addressed'])]), axis=1)

            # Use fuzzywuzzy to find the best match for the provided title
            best_matches = process.extract(title, df['combined'], limit=3)

            if best_matches:
                # Get the corresponding procurements from the best match
                response = "I found the following procurements related to '{}':\n".format(title)
                for match in best_matches:
                    matched_combined = match[0]
                    # Find the index of the best match in the DataFrame
                    matched_idx = df[df['combined'] == matched_combined].index[0]
                    procurement = df.iloc[matched_idx]
                    
                    response += (
                        f"- **Title**: {procurement['title']}\n"
                        f"  **Description**: {procurement['description']}\n"
                        f"  **Skills**: {', '.join(procurement['skills'])}\n"
                        f"  **Experience**: {', '.join(procurement['experience'])}\n"
                        f"  **Challenges Addressed**: {', '.join(procurement['challenges_addressed'])}\n\n"
                    )
                
                # Trim the response if too long
                if len(response) > 2000:  # Adjust length based on your platform's message limits
                    response = response[:2000] + '...'
                    
                dispatcher.utter_message(text=response)
            else:
                dispatcher.utter_message(f"Sorry, I couldn't find any procurements related to '{title}'. I’m still learning more about this.")
        else:
            dispatcher.utter_message("I'm sorry, I didn't catch the title you're looking for. Please try again and provide a title.")

        return []

# Handle irrelevant queries
class ActionHandleIrrelevant(Action):

    def name(self) -> Text:
        return "action_handle_irrelevant"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        irrelevant_responses = [
            "I’m here to assist with relevant queries. Is there something specific you need help with?",
            "That’s interesting! I specialize in providing information and answering questions. How can I assist you today?",
            "I can’t help with that, but if you have any specific questions or need assistance, I’m here for you.",
            "I’m here to help with specific information or queries. Please let me know if there’s anything else you need.",
            "I understand, but my expertise is in providing specific information and assistance. How can I help you further?"
        ]
        response = random.choice(irrelevant_responses)
        dispatcher.utter_message(response)
        return []

# Handle intro queries        
class ActionHandleIntroductionQueries(Action):
    def name(self) -> Text:
        return "action_handle_introduction_queries"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user_message = tracker.latest_message.get('text', '').lower()
        
        introduction_responses = [
            "I’m a virtual assistant designed to help you find and search for procurements across various industries and sectors. With access to over 500 procurements, I can provide detailed information and assist you in locating relevant opportunities. How can I assist you today?",
            "I’m here to help you navigate through a vast database of procurements available in different industries and expertise areas. Whether you’re looking for procurement opportunities or need information about specific sectors, I’m here to assist. What would you like to know more about?",
            "I specialize in providing information about procurements across a wide range of sectors and expertise. With our comprehensive database of over 500 procurements, I can help you find detailed and relevant information based on your needs. How can I assist you today?",
            "As an assistant focused on procurement information, I can help you search for and explore various procurement opportunities available across different industries. If you need details about specific procurements or want to know more about a certain sector, feel free to ask!",
            "My primary role is to assist you in finding and searching for procurements in various sectors and industries. With a broad range of over 500 procurements at my disposal, I’m here to provide the information you need. Let me know how I can help with your procurement search!",
            "I’m here to support your search for procurement opportunities across multiple industries and expertise areas. With access to a comprehensive list of procurements, I can help you locate and understand relevant procurement information. How can I assist you in your search today?"
        ]

        # Determine if the message is an introduction query
        introduction_keywords = [
            "what is this", "who are you", "what about you", "what are you", 
            "are you a bot", "are you human", "tell me about yourself", 
            "what can you do", "what do you do", "what's your purpose"
        ]
        
        if any(keyword in user_message for keyword in introduction_keywords):
            response = random.choice(introduction_responses)
        else:
            response = "I’m here to help you with procurement-related queries. How can I assist you today?"

        dispatcher.utter_message(text=response)
        return []