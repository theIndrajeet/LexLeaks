import os
import httpx
from typing import Optional, Dict, Any, List
import json
from datetime import datetime
import re

class IndianKanoonService:
    def __init__(self):
        self.api_key = os.getenv("INDIAN_KANOON_API_KEY", "2d3d2197f744e6e3fe52e626a54bc47640ee0f30")
        self.base_url = "https://api.indiankanoon.org"
        self.headers = {
            "Authorization": f"Token {self.api_key}",
            "Accept": "application/json"
        }
    
    async def search_cases(
        self, 
        query: str, 
        page: int = 0, 
        court_type: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search for legal cases using Indian Kanoon API
        
        Args:
            query: Search query (case title, keywords, etc.)
            page: Page number (starting from 0)
            court_type: Filter by court type (optional)
            date_from: Start date filter (DD-MM-YYYY format)
            date_to: End date filter (DD-MM-YYYY format)
        
        Returns:
            Dictionary containing search results
        """
        try:
            # Build search URL according to API documentation
            search_url = f"{self.base_url}/search/"
            params = {
                "formInput": query,
                "pagenum": page
            }
            
            # Add optional filters
            if court_type:
                params["doctypes"] = court_type
            if date_from:
                params["fromdate"] = date_from
            if date_to:
                params["todate"] = date_to
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(search_url, headers=self.headers, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                # Parse the API response according to documentation
                cases = []
                if "docs" in data:
                    for doc in data["docs"]:
                        cases.append({
                            "doc_id": str(doc.get("tid", "")),
                            "title": doc.get("title", ""),
                            "court": doc.get("docsource", "Unknown Court"),
                            "date": doc.get("publishdate", "Unknown Date"),
                            "snippet": doc.get("headline", ""),
                            "url": f"https://indiankanoon.org/doc/{doc.get('tid', '')}/",
                            "citation": doc.get("citation", doc.get("docsource", ""))
                        })
                
                # Parse the "found" field to extract total count
                found_text = data.get("found", "0")
                total_results = 0
                if found_text and isinstance(found_text, str):
                    # Extract number from "1 - 10 of 360970" format
                    import re
                    match = re.search(r'of (\d+)', found_text)
                    if match:
                        total_results = int(match.group(1))
                    else:
                        total_results = len(cases)
                else:
                    total_results = len(cases)
                
                return {
                    "success": True,
                    "query": query,
                    "page": page,
                    "total_results": total_results,
                    "cases": cases,
                    "error": None
                }
                    
        except httpx.TimeoutException:
            return {
                "success": False,
                "error": "Request timeout - Indian Kanoon API is taking too long to respond"
            }
        except httpx.RequestError as e:
            return {
                "success": False,
                "error": f"Network error: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }
    
    
    async def get_case_details(self, doc_id: str) -> Dict[str, Any]:
        """
        Get full details of a specific case using Indian Kanoon API

        Args:
            doc_id: Document ID from search results

        Returns:
            Dictionary containing case details
        """
        try:
            # Use the document API endpoint according to documentation
            doc_url = f"{self.base_url}/doc/{doc_id}/"
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(doc_url, headers=self.headers)
                response.raise_for_status()
                
                data = response.json()
                
                # Parse the API response according to documentation
                return {
                    "success": True,
                    "doc_id": doc_id,
                    "title": data.get("title", ""),
                    "court": data.get("docsource", "Unknown Court"),
                    "date": data.get("date", "Unknown Date"),
                    "judges": data.get("bench", []),
                    "parties": data.get("parties", []),
                    "content": data.get("doc", ""),  # The main document content
                    "citations": data.get("citeList", []),
                    "url": f"https://indiankanoon.org/doc/{doc_id}/",
                    "related_cases": data.get("citedbyList", []),
                    "error": None
                }

        except httpx.TimeoutException:
            return {
                "success": False,
                "error": "Request timeout - Indian Kanoon API is taking too long to respond"
            }
        except httpx.RequestError as e:
            return {
                "success": False,
                "error": f"Network error: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }
    
    async def get_case_original(self, doc_id: str) -> Dict[str, Any]:
        """
        Get original document of a case (higher cost but complete text)
        
        Args:
            doc_id: Document ID from search results
        
        Returns:
            Dictionary containing original case document
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/doc/{doc_id}/original/",
                    headers=self.headers,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    return {
                        "success": True,
                        "data": response.json(),
                        "doc_id": doc_id
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Failed to fetch original document. Status: {response.status_code}",
                        "details": response.text
                    }
                    
        except httpx.TimeoutException:
            return {
                "success": False,
                "error": "Request timeout - Indian Kanoon API is taking too long to respond"
            }
        except httpx.RequestError as e:
            return {
                "success": False,
                "error": f"Network error: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }
    
    def format_search_results(self, raw_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format search results for frontend consumption
        
        Args:
            raw_results: Raw API response from Indian Kanoon
        
        Returns:
            Formatted results with clean structure
        """
        if not raw_results.get("success"):
            return raw_results
        
        try:
            data = raw_results["data"]
            formatted_results = {
                "success": True,
                "query": raw_results.get("query", ""),
                "page": raw_results.get("page", 0),
                "total_results": data.get("total", 0),
                "cases": []
            }
            
            # Process each case in the results
            for case in data.get("results", []):
                formatted_case = {
                    "doc_id": case.get("doc_id", ""),
                    "title": case.get("title", ""),
                    "court": case.get("court", ""),
                    "date": case.get("date", ""),
                    "judges": case.get("judges", []),
                    "snippet": case.get("snippet", ""),
                    "url": case.get("url", ""),
                    "citation": case.get("citation", "")
                }
                formatted_results["cases"].append(formatted_case)
            
            return formatted_results
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error formatting results: {str(e)}"
            }
    
    def format_case_details(self, raw_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format case details for frontend consumption
        
        Args:
            raw_details: Raw API response from Indian Kanoon
        
        Returns:
            Formatted case details with clean structure
        """
        if not raw_details.get("success"):
            return raw_details
        
        try:
            data = raw_details["data"]
            formatted_details = {
                "success": True,
                "doc_id": raw_details.get("doc_id", ""),
                "title": data.get("title", ""),
                "court": data.get("court", ""),
                "date": data.get("date", ""),
                "judges": data.get("judges", []),
                "parties": data.get("parties", []),
                "content": data.get("content", ""),
                "citations": data.get("citations", []),
                "url": data.get("url", ""),
                "related_cases": data.get("related_cases", [])
            }
            
            return formatted_details
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error formatting case details: {str(e)}"
            }
    
    def _get_enhanced_search_results(self, query: str, page: int, court_type: Optional[str] = None, date_from: Optional[str] = None, date_to: Optional[str] = None) -> Dict[str, Any]:
        """
        Return enhanced mock search results with realistic legal case data
        """
        # Generate realistic case data based on query
        base_cases = [
            {
                "doc_id": f"SC{2023 + page}{1000 + page * 10 + 1}",
                "title": f"State of Maharashtra vs. {query.title()} - Constitutional Challenge",
                "court": "Supreme Court of India",
                "date": "2023-01-15",
                "judges": ["Justice D. Y. Chandrachud", "Justice S. Ravindra Bhat"],
                "snippet": f"The Supreme Court examined the constitutional validity of provisions related to {query} in the context of fundamental rights and state powers.",
                "url": f"https://indiankanoon.org/doc/SC{2023 + page}{1000 + page * 10 + 1}/",
                "citation": f"2023 SCC {1 + page}"
            },
            {
                "doc_id": f"HC{2023 + page}{2000 + page * 10 + 2}",
                "title": f"Public Interest Litigation: {query.title()} and Environmental Rights",
                "court": "Delhi High Court",
                "date": "2023-02-20",
                "judges": ["Justice S. Muralidhar", "Justice Vibhu Bakhru"],
                "snippet": f"A public interest litigation challenging the implementation of {query} policies and their impact on environmental protection and public health.",
                "url": f"https://indiankanoon.org/doc/HC{2023 + page}{2000 + page * 10 + 2}/",
                "citation": f"2023 DLH {2 + page}"
            },
            {
                "doc_id": f"SC{2023 + page}{3000 + page * 10 + 3}",
                "title": f"Landmark Judgment: {query.title()} and Human Rights Protection",
                "court": "Supreme Court of India",
                "date": "2023-03-10",
                "judges": ["Justice N. V. Ramana", "Justice Hima Kohli", "Justice B. V. Nagarathna"],
                "snippet": f"A landmark judgment establishing important precedents regarding {query} and its implications for human rights protection and constitutional interpretation.",
                "url": f"https://indiankanoon.org/doc/SC{2023 + page}{3000 + page * 10 + 3}/",
                "citation": f"2023 SCC {3 + page}"
            },
            {
                "doc_id": f"HC{2023 + page}{4000 + page * 10 + 4}",
                "title": f"Commercial Dispute: {query.title()} in Corporate Law",
                "court": "Bombay High Court",
                "date": "2023-04-05",
                "judges": ["Justice G. S. Patel", "Justice N. J. Jamadar"],
                "snippet": f"A commercial dispute involving {query} and its application in corporate governance, shareholder rights, and regulatory compliance.",
                "url": f"https://indiankanoon.org/doc/HC{2023 + page}{4000 + page * 10 + 4}/",
                "citation": f"2023 Bom HC {4 + page}"
            },
            {
                "doc_id": f"SC{2023 + page}{5000 + page * 10 + 5}",
                "title": f"Criminal Law: {query.title()} and Due Process Rights",
                "court": "Supreme Court of India",
                "date": "2023-05-12",
                "judges": ["Justice U. U. Lalit", "Justice S. Abdul Nazeer"],
                "snippet": f"An important criminal law case examining {query} in the context of due process rights, fair trial guarantees, and criminal justice reform.",
                "url": f"https://indiankanoon.org/doc/SC{2023 + page}{5000 + page * 10 + 5}/",
                "citation": f"2023 SCC {5 + page}"
            }
        ]
        
        # Filter by court type if specified
        if court_type:
            if court_type == "supreme":
                base_cases = [case for case in base_cases if "Supreme Court" in case["court"]]
            elif court_type == "high":
                base_cases = [case for case in base_cases if "High Court" in case["court"]]
            elif court_type == "district":
                base_cases = [case for case in base_cases if "District Court" in case["court"]]
        
        # Add more cases for pagination
        total_cases = 25 + page * 10
        all_cases = base_cases * (total_cases // len(base_cases) + 1)
        all_cases = all_cases[:total_cases]
        
        return {
            "success": True,
            "data": {
                "total": total_cases,
                "results": all_cases
            },
            "query": query,
            "page": page
        }
    
    def _get_mock_search_results(self, query: str, page: int) -> Dict[str, Any]:
        """
        Return mock search results for testing when API is not available
        """
        return self._get_enhanced_search_results(query, page)
    
    def _get_enhanced_case_details(self, doc_id: str) -> Dict[str, Any]:
        """
        Return enhanced mock case details with realistic legal content
        """
        # Generate realistic case details based on doc_id
        case_templates = [
            {
                "title": f"State of Maharashtra vs. Constitutional Rights - Document {doc_id}",
                "court": "Supreme Court of India",
                "date": "2023-01-15",
                "judges": ["Justice D. Y. Chandrachud", "Justice S. Ravindra Bhat"],
                "parties": [
                    "Petitioner: State of Maharashtra, represented by Advocate General",
                    "Respondent: Citizens' Rights Foundation, represented by Senior Advocate",
                    "Intervenor: National Human Rights Commission"
                ],
                "content": f"""
                <h2>JUDGMENT</h2>
                
                <p><strong>D. Y. Chandrachud, J.</strong> - This case presents a significant constitutional question regarding the scope and application of fundamental rights in the context of state action. The matter has been referred to this Bench for consideration of important legal principles that have far-reaching implications for the protection of individual liberties.</p>
                
                <h3>Facts of the Case</h3>
                <p>The present case arises from a challenge to certain provisions of state legislation that purport to regulate the exercise of fundamental rights guaranteed under Part III of the Constitution. The petitioners have raised serious concerns about the constitutional validity of these provisions, arguing that they impose unreasonable restrictions on the exercise of fundamental freedoms.</p>
                
                <p>The dispute originated when the State of Maharashtra enacted the Public Safety and Security Act, 2022, which contained several provisions that directly impacted the exercise of fundamental rights. The petitioners, representing various civil society organizations and affected individuals, filed a writ petition under Article 32 of the Constitution challenging the constitutional validity of these provisions.</p>
                
                <p>The impugned legislation was enacted in response to growing concerns about public safety and national security. However, the petitioners argue that the legislation goes far beyond what is necessary to achieve these legitimate objectives and imposes disproportionate restrictions on fundamental rights.</p>
                
                <h3>Legal Issues</h3>
                <p>The following questions of law arise for consideration:</p>
                <ol>
                    <li>Whether the impugned provisions violate the fundamental rights guaranteed under Articles 19 and 21 of the Constitution;</li>
                    <li>Whether the restrictions imposed are reasonable and fall within the permissible limits of constitutional scrutiny;</li>
                    <li>Whether the state has demonstrated a compelling state interest that justifies the restrictions imposed;</li>
                    <li>Whether the legislation meets the test of proportionality as laid down by this Court;</li>
                    <li>Whether the procedural safeguards provided in the legislation are adequate to protect individual rights.</li>
                </ol>
                
                <h3>Analysis and Reasoning</h3>
                <p>In examining the constitutional validity of the impugned provisions, this Court must apply the well-established principles of constitutional interpretation. The fundamental rights enshrined in Part III of the Constitution are not absolute and are subject to reasonable restrictions as provided in the Constitution itself.</p>
                
                <p>However, any restriction on fundamental rights must satisfy the test of reasonableness as laid down in various decisions of this Court. The restriction must be:</p>
                <ul>
                    <li>In the interest of public order, morality, or health;</li>
                    <li>Reasonable in nature and extent;</li>
                    <li>Not arbitrary or discriminatory;</li>
                    <li>Proportionate to the legitimate aim sought to be achieved.</li>
                </ul>
                
                <p>This Court has consistently held that the right to freedom of speech and expression under Article 19(1)(a) is a cornerstone of democracy. Any restriction on this right must be carefully scrutinized to ensure that it does not unduly curtail the democratic discourse that is essential for the functioning of a free society.</p>
                
                <p>Similarly, the right to life and personal liberty under Article 21 has been interpreted expansively by this Court to include various facets of human dignity and freedom. Any legislation that seeks to restrict these rights must demonstrate a compelling state interest and must be the least restrictive means available to achieve the stated objective.</p>
                
                <p>In the present case, while the state has a legitimate interest in ensuring public safety and national security, the impugned provisions appear to be overly broad and disproportionate to the stated objectives. The legislation grants extensive powers to the executive without adequate safeguards to prevent abuse.</p>
                
                <h3>Precedents and Case Law</h3>
                <p>This Court has consistently emphasized the importance of balancing individual rights with state interests. In the landmark case of Maneka Gandhi v. Union of India, this Court held that any procedure that deprives a person of their life or personal liberty must be fair, just, and reasonable.</p>
                
                <p>Similarly, in the case of S. R. Bommai v. Union of India, this Court emphasized that the Constitution is not a document of convenience but a charter of rights that must be protected against arbitrary state action.</p>
                
                <p>More recently, in the case of Justice K. S. Puttaswamy v. Union of India, this Court recognized the right to privacy as a fundamental right and emphasized the need for strict scrutiny of any legislation that seeks to restrict this right.</p>
                
                <h3>International Perspective</h3>
                <p>The principles of proportionality and necessity in restricting fundamental rights are well-established in international human rights law. The European Court of Human Rights has consistently held that any restriction on fundamental rights must be necessary in a democratic society and must be proportionate to the legitimate aim pursued.</p>
                
                <p>Similarly, the United Nations Human Rights Committee has emphasized that restrictions on fundamental rights must be narrowly tailored and must not undermine the essence of the right itself.</p>
                
                <h3>Conclusion</h3>
                <p>After careful consideration of the arguments advanced by both parties and the legal principles applicable to the case, this Court is of the opinion that the impugned provisions, to the extent they impose unreasonable restrictions on fundamental rights, are unconstitutional and must be struck down.</p>
                
                <p>The State is directed to take appropriate measures to bring the legislation in conformity with constitutional requirements within a period of six months from the date of this judgment. The State may, if it so desires, re-enact the legislation with appropriate modifications to address the constitutional concerns raised in this judgment.</p>
                
                <p>This Court further directs that until the legislation is brought in conformity with constitutional requirements, the impugned provisions shall remain suspended and shall not be enforced against any person.</p>
                
                <p>The writ petition is allowed in the above terms. There shall be no order as to costs.</p>
                """,
                "citations": ["2023 SCC 1", "AIR 2023 SC 100", "2023 (1) SCALE 1"],
                "url": f"https://indiankanoon.org/doc/{doc_id}/",
                "related_cases": [f"SC{2023}2001", f"HC{2023}3002", f"SC{2023}4003"]
            },
            {
                "title": f"Public Interest Litigation: Environmental Rights - Document {doc_id}",
                "court": "Delhi High Court",
                "date": "2023-02-20",
                "judges": ["Justice S. Muralidhar", "Justice Vibhu Bakhru"],
                "parties": [
                    "Petitioner: Environmental Protection Society",
                    "Respondent: Union of India, Ministry of Environment and Forests",
                    "Respondent: State Pollution Control Board"
                ],
                "content": f"""
                <h2>JUDGMENT</h2>
                
                <p><strong>S. Muralidhar, J.</strong> - This public interest litigation raises important questions concerning environmental protection and the right to a clean and healthy environment, which has been recognized as a fundamental right under Article 21 of the Constitution.</p>
                
                <h3>Background</h3>
                <p>The petitioner, a registered society working for environmental protection, has approached this Court seeking directions for the effective implementation of environmental laws and regulations. The petition highlights various instances of environmental degradation and the failure of authorities to take appropriate remedial measures.</p>
                
                <p>The petition was filed in response to alarming reports of environmental pollution in the National Capital Region, particularly affecting the air quality and water resources. The petitioner has documented numerous violations of environmental laws by industrial units, construction projects, and other activities that have resulted in severe environmental degradation.</p>
                
                <p>Despite repeated representations to various authorities, including the Central Pollution Control Board, State Pollution Control Board, and municipal authorities, no effective action has been taken to address the environmental concerns raised by the petitioner.</p>
                
                <h3>Legal Framework</h3>
                <p>The right to a clean and healthy environment is now well-established as a fundamental right under Article 21 of the Constitution. This right encompasses the right to clean air, water, and soil, and the right to be free from environmental pollution that affects the quality of life.</p>
                
                <p>This Court has consistently held that environmental protection is not just a policy objective but a constitutional mandate. In the landmark case of M. C. Mehta v. Union of India, this Court recognized the right to a clean environment as a fundamental right and emphasized the duty of the state to protect and improve the environment.</p>
                
                <p>The Environment (Protection) Act, 1986, the Air (Prevention and Control of Pollution) Act, 1981, and the Water (Prevention and Control of Pollution) Act, 1974, provide the statutory framework for environmental protection. These laws impose specific obligations on industries and other polluting activities to ensure compliance with environmental standards.</p>
                
                <h3>Environmental Impact Assessment</h3>
                <p>The petition highlights several critical environmental issues that require immediate attention:</p>
                <ul>
                    <li>Severe air pollution exceeding permissible limits in residential areas</li>
                    <li>Contamination of groundwater due to improper disposal of industrial waste</li>
                    <li>Deforestation and loss of green cover due to unregulated construction</li>
                    <li>Noise pollution from industrial activities affecting residential areas</li>
                    <li>Improper handling and disposal of hazardous waste materials</li>
                </ul>
                
                <p>The environmental impact assessment conducted by independent experts reveals that the current levels of pollution pose serious health risks to the local population, particularly children and the elderly. The assessment also indicates that the environmental damage is largely irreversible and will have long-term consequences for the ecosystem.</p>
                
                <h3>International Obligations</h3>
                <p>India is a signatory to various international environmental conventions, including the United Nations Framework Convention on Climate Change and the Convention on Biological Diversity. These international obligations require India to take effective measures to protect the environment and promote sustainable development.</p>
                
                <p>The principle of sustainable development, which balances economic development with environmental protection, has been recognized as a fundamental principle of environmental law. This principle requires that development activities must not compromise the ability of future generations to meet their own needs.</p>
                
                <h3>Directions Issued</h3>
                <p>In view of the serious environmental concerns raised in the petition, this Court issues the following directions:</p>
                <ol>
                    <li>The State Pollution Control Board shall conduct a comprehensive environmental audit of all industrial units in the area within three months and submit a detailed report to this Court;</li>
                    <li>Strict compliance with environmental standards shall be ensured, and non-compliant units shall be directed to shut down operations until they achieve compliance;</li>
                    <li>A monitoring committee shall be constituted under the chairmanship of a retired High Court Judge to oversee the implementation of environmental protection measures;</li>
                    <li>All construction projects in the area shall be subject to mandatory environmental clearance and shall implement green building standards;</li>
                    <li>The municipal authorities shall ensure proper waste management and implement measures to reduce air pollution from vehicular traffic;</li>
                    <li>Regular monitoring of air and water quality shall be conducted, and the results shall be made publicly available;</li>
                    <li>Environmental education and awareness programs shall be conducted for the local population to promote environmental consciousness.</li>
                </ol>
                
                <h3>Implementation and Monitoring</h3>
                <p>The monitoring committee shall submit quarterly reports to this Court on the progress of implementation of the directions issued. The committee shall have the power to recommend additional measures if necessary and shall coordinate with all relevant authorities to ensure effective implementation.</p>
                
                <p>Any violation of the directions issued by this Court shall be treated as contempt of court and shall be dealt with accordingly. The authorities are directed to take immediate action against any person or entity found to be violating environmental laws or the directions issued by this Court.</p>
                
                <h3>Conclusion</h3>
                <p>Environmental protection is a constitutional obligation that cannot be compromised. The right to a clean and healthy environment is fundamental to the right to life and must be protected at all costs. This Court expects all authorities to work together to ensure effective implementation of environmental protection measures.</p>
                
                <p>The writ petition is allowed in the above terms. The monitoring committee shall be constituted within one month from the date of this judgment. There shall be no order as to costs.</p>
                """,
                "citations": ["2023 DLH 2", "2023 (2) DLT 1"],
                "url": f"https://indiankanoon.org/doc/{doc_id}/",
                "related_cases": [f"SC{2023}5004", f"HC{2023}6005"]
            }
        ]
        
        # Select template based on doc_id
        template = case_templates[hash(doc_id) % len(case_templates)]
        
        return {
            "success": True,
            "data": template,
            "doc_id": doc_id
        }
    
    def _get_mock_case_details(self, doc_id: str) -> Dict[str, Any]:
        """
        Return mock case details for testing when API is not available
        """
        return self._get_enhanced_case_details(doc_id)
