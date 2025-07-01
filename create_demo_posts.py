#!/usr/bin/env python3
"""
Create demo posts for LexLeaks platform
"""

import requests
import json
from datetime import datetime, timedelta
import random

# API configuration
API_BASE_URL = "http://localhost:8000"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "LexLeaks2024!"

# Demo posts data
DEMO_POSTS = [
    {
        "title": "The 'Unlimited Leave' Policy with a Hidden Clause",
        "slug": "unlimited-leave-policy-hidden-clause",
        "excerpt": "A deep dive into the employment contracts of three major tech startups reveals how 'unlimited' leave policies can paradoxically lead to employees taking less time off, and the subtle legal language that makes it possible.",
        "content": """<p>Our investigation into employment contracts at three prominent tech startups has uncovered a troubling pattern in their "unlimited" paid time off (PTO) policies. While marketed as a progressive benefit, these policies contain hidden clauses that effectively discourage employees from taking time off.</p>

<h2>The Fine Print</h2>
<p>Buried in Section 4.3.2 of the standard employment agreement at TechCorp (name changed for legal reasons), we found this critical clause:</p>

<blockquote>"Employee acknowledges that time off is subject to manager approval based on business needs and project deliverables. Excessive time off, as determined by management discretion, may impact performance evaluations and bonus eligibility."</blockquote>

<p>The term "excessive" is never defined, leaving it entirely to management's interpretation. Our sources report that employees who took more than 10 days off in a year received negative performance reviews, despite the "unlimited" policy.</p>

<h2>The Psychology of Ambiguity</h2>
<p>Dr. Sarah Chen, an employment law expert at Stanford, explains: "When there's no clear limit, employees often take less time off because they don't know what's acceptable. Traditional PTO policies with clear allocations actually result in more time off taken."</p>

<h2>The Data Speaks</h2>
<p>Internal documents obtained from these companies show:</p>
<ul>
<li>Average time off taken under "unlimited" policy: 9.3 days/year</li>
<li>Average time off taken under traditional 15-day policy: 13.8 days/year</li>
<li>48% decrease in vacation days taken after switching to "unlimited"</li>
</ul>

<h2>Legal Implications</h2>
<p>Several employees have filed complaints with the Department of Labor, arguing that the "unlimited" label constitutes false advertising. Attorney Michael Rodriguez, representing five former employees, states: "These policies are designed to reduce company liability for unused PTO while psychologically manipulating employees into taking less time off."</p>

<h2>What You Can Do</h2>
<p>If you're evaluating a job offer with "unlimited" PTO:</p>
<ol>
<li>Ask for the specific policy language in writing</li>
<li>Request data on average PTO taken by employees</li>
<li>Look for any clauses linking time off to performance reviews</li>
<li>Consider negotiating for a traditional PTO structure instead</li>
</ol>

<p><em>Have you experienced similar issues with "unlimited" PTO policies? Contact us securely to share your story.</em></p>""",
        "status": "published",
        "published_at": datetime.now() - timedelta(days=3)
    },
    {
        "title": "Privacy Violations in Food Delivery Apps: What Your Data is Really Used For",
        "slug": "privacy-violations-food-delivery-apps",
        "excerpt": "Internal documents reveal that a popular food delivery service shares extensive user data with third-party marketing firms, going far beyond what's disclosed in their privacy policy.",
        "content": """<p>LexLeaks has obtained internal documents from QuickBite (name changed), one of India's largest food delivery platforms, revealing systematic violations of user privacy that potentially affect millions of customers.</p>

<h2>The Data Collection Scheme</h2>
<p>According to the leaked documents dated March 2024, QuickBite collects and shares:</p>
<ul>
<li>Real-time location data (even when app is closed)</li>
<li>Complete order history with dietary preferences</li>
<li>Payment methods and spending patterns</li>
<li>Device contacts and social connections</li>
<li>Browsing history within the app</li>
</ul>

<h2>Third-Party Data Sharing</h2>
<p>The most alarming revelation is the extent of data sharing with marketing firms. A confidential agreement with DataMine Analytics shows that QuickBite provides:</p>

<blockquote>"Comprehensive user profiles including dietary restrictions, income estimates based on order patterns, family size estimates, and lifestyle categorizations for targeted advertising purposes."</blockquote>

<h2>Beyond the Privacy Policy</h2>
<p>While QuickBite's privacy policy mentions "sharing data with partners," it fails to disclose:</p>
<ul>
<li>The creation of "shadow profiles" for non-users mentioned in delivery addresses</li>
<li>Sale of aggregated neighborhood dining patterns to restaurant chains</li>
<li>Sharing of user movement patterns with retail companies</li>
</ul>

<h2>Legal Violations</h2>
<p>Privacy lawyer Priya Sharma notes: "This appears to violate India's Information Technology Act and potentially the upcoming Data Protection Bill. Users have not consented to this level of data exploitation."</p>

<h2>The Health Data Angle</h2>
<p>Most concerning is the inference of health conditions from food orders. Internal emails show discussions about identifying diabetic users based on sugar-free preferences and selling this data to insurance companies.</p>

<h2>Company Response</h2>
<p>When approached for comment, QuickBite provided a standard statement about "taking privacy seriously" but did not address specific allegations.</p>

<h2>Protecting Yourself</h2>
<p>Until regulations catch up:</p>
<ol>
<li>Limit app permissions (especially location)</li>
<li>Use cash payments when possible</li>
<li>Avoid saving addresses in the app</li>
<li>Consider using fake names for orders</li>
<li>Regularly clear app data and cache</li>
</ol>

<p><em>We have shared these findings with the relevant authorities. If you have information about data misuse by tech companies, please reach out through our secure channels.</em></p>""",
        "status": "published",
        "published_at": datetime.now() - timedelta(days=5)
    },
    {
        "title": "The Shady Side of LegalTech: AI Contract Review Tools Storing Client Data",
        "slug": "legaltech-ai-contract-review-data-retention",
        "excerpt": "Several AI-powered contract review platforms retain copies of uploaded legal documents for 'model training,' raising serious questions about client confidentiality and attorney-client privilege.",
        "content": """<p>A LexLeaks investigation has uncovered that multiple AI-powered legal technology platforms are secretly retaining and analyzing confidential legal documents uploaded by law firms, potentially violating attorney-client privilege on a massive scale.</p>

<h2>The Discovery</h2>
<p>While reviewing the terms of service for ContractAI Pro, LegalBot, and SmartReview (names changed), our team discovered buried clauses granting these companies broad rights to retain and use uploaded documents. A whistleblower from one of these companies provided us with internal documentation confirming our worst fears.</p>

<h2>What's Really Happening</h2>
<p>According to leaked internal memos:</p>
<ul>
<li>All uploaded contracts are permanently stored in cloud databases</li>
<li>Documents are used to train AI models without client consent</li>
<li>Metadata including party names, deal values, and terms are extracted and aggregated</li>
<li>Some platforms sell "market intelligence" based on this data</li>
</ul>

<h2>The Legal Minefield</h2>
<p>Professor James Liu from Harvard Law School explains the severity: "This is a fundamental breach of the attorney-client privilege. Lawyers using these tools may be unknowingly waiving privilege for their clients' most sensitive documents."</p>

<h2>Real-World Impact</h2>
<p>We've identified several cases where this data retention had serious consequences:</p>

<blockquote><strong>Case 1:</strong> A merger agreement uploaded to LegalBot was found in the training data of a competitor's AI model, leading to leaked deal terms.</blockquote>

<blockquote><strong>Case 2:</strong> Confidential settlement agreements from multiple law firms were discovered in ContractAI Pro's "example database."</blockquote>

<h2>The Technical Deception</h2>
<p>These platforms claim to use "federated learning" and "differential privacy," but internal documents reveal these protections are minimal. One engineer's email states: "We need the raw data for the models to work well. The privacy stuff is mostly marketing."</p>

<h2>Regulatory Blind Spot</h2>
<p>Currently, no specific regulations govern AI platforms handling legal documents. The American Bar Association has issued warnings, but enforcement remains unclear.</p>

<h2>Hidden Terms of Service</h2>
<p>Buried in Section 14.2.1 of ContractAI Pro's 47-page terms of service:</p>

<blockquote>"By uploading content, user grants Company a perpetual, irrevocable, worldwide license to use, modify, and create derivative works from uploaded materials for product improvement and machine learning purposes."</blockquote>

<h2>What Law Firms Must Do</h2>
<ol>
<li>Immediately audit all LegalTech tools for data retention policies</li>
<li>Obtain explicit client consent before using AI tools</li>
<li>Demand data deletion capabilities and audit trails</li>
<li>Consider on-premise solutions only</li>
<li>Review malpractice insurance coverage for AI-related breaches</li>
</ol>

<h2>The Whistleblower's Warning</h2>
<p>Our source, a senior developer at one of these companies, warns: "Law firms have no idea what they're agreeing to. We have contracts from Fortune 500 deals, government agreements, everything. It's a ticking time bomb."</p>

<p><em>If you work in LegalTech and have concerns about data handling practices, contact us through our secure submission system.</em></p>""",
        "status": "published",
        "published_at": datetime.now() - timedelta(days=7)
    },
    {
        "title": "Judge's Undisclosed Conflict of Interest in Major Environmental Case",
        "slug": "judge-conflict-of-interest-environmental-case",
        "excerpt": "Financial documents reveal that a federal judge presiding over a landmark environmental lawsuit held significant investments in the defendant company through a complex trust structure.",
        "content": """<p>LexLeaks has obtained financial records showing that Judge Robert Harrison (name changed) of the District Court failed to disclose substantial financial interests in Titan Industries while presiding over a major environmental contamination case against the company.</p>

<h2>The Hidden Investment</h2>
<p>Through a series of shell companies and family trusts, Judge Harrison indirectly owned approximately $2.3 million in Titan Industries stock. The investment was structured through:</p>
<ul>
<li>The Harrison Family Revocable Trust</li>
<li>Blue Mountain Investment LLC (owned by the trust)</li>
<li>Diversified Holdings Fund (which held Titan Industries stock)</li>
</ul>

<h2>The Case at Stake</h2>
<p>The lawsuit, filed by residents of Riverside County, alleged that Titan Industries contaminated groundwater affecting 15,000 residents. Potential damages were estimated at $500 million. Judge Harrison consistently ruled in favor of Titan Industries on key motions, ultimately dismissing the case on technical grounds.</p>

<h2>Pattern of Favorable Rulings</h2>
<p>Our analysis of Judge Harrison's decisions shows:</p>
<ul>
<li>Denied 8 out of 9 discovery requests from plaintiffs</li>
<li>Granted all 6 summary judgment motions from Titan Industries</li>
<li>Excluded key expert testimony on contamination levels</li>
<li>Ultimately dismissed the case citing "lack of standing"</li>
</ul>

<h2>The Disclosure Failure</h2>
<p>Federal law requires judges to recuse themselves from cases where they have a financial interest exceeding $15,000. Judge Harrison's annual disclosure forms listed the family trust but not its underlying investments.</p>

<h2>Legal Ethics Violated</h2>
<p>Professor Amanda Chen from Yale Law School states: "This is a textbook violation of judicial ethics. The structure of the investment appears designed to obscure the conflict of interest."</p>

<h2>Previous Patterns</h2>
<p>Our investigation found this isn't isolated:</p>
<ul>
<li>3 other environmental cases with similar favorable rulings</li>
<li>All involved companies in which the trust held investments</li>
<li>Total value of investments in these companies: $8.7 million</li>
</ul>

<h2>The Victims' Perspective</h2>
<p>Maria Gonzalez, lead plaintiff in the Riverside case, told LexLeaks: "We knew something was wrong when every single ruling went against us. Now we know why. My children are still drinking bottled water because our wells are contaminated."</p>

<h2>Calls for Investigation</h2>
<p>Several legal ethics organizations are calling for:</p>
<ul>
<li>Full investigation by the Judicial Conference</li>
<li>Review of all cases handled by Judge Harrison</li>
<li>Criminal investigation for potential fraud</li>
<li>Reform of judicial disclosure requirements</li>
</ul>

<p><em>This investigation is ongoing. If you have information about judicial conflicts of interest, please contact us securely.</em></p>""",
        "status": "published",
        "published_at": datetime.now() - timedelta(days=10)
    },
    {
        "title": "Law Firm's Secret Commission Deal with Litigation Funders",
        "slug": "law-firm-secret-commission-litigation-funders",
        "excerpt": "Internal emails expose how a prestigious law firm received undisclosed kickbacks from litigation funding companies while advising clients to accept unfavorable funding terms.",
        "content": """<p>ARCHIVED - This older investigation remains relevant as similar practices continue in the litigation funding industry.</p>

<p>Leaked emails from Morrison & Associates (name changed), a top-tier law firm, reveal a systematic scheme to receive secret commissions from litigation funding companies while advising clients to accept these same funders' offers.</p>

<h2>The Scheme Exposed</h2>
<p>According to internal emails between partners:</p>
<ul>
<li>The firm received 5-8% commission on all funded cases</li>
<li>Commissions were hidden through "consulting fees"</li>
<li>Clients were told the firm had "no financial relationship" with funders</li>
<li>Over $12 million in secret commissions over 3 years</li>
</ul>

<h2>How It Worked</h2>
<p>Email from Senior Partner James Morrison to litigation funding team:</p>
<blockquote>"Remember, we need to maintain the appearance of independence. All commission payments should be routed through the consulting agreement with M&A Advisory Services LLC. Under no circumstances should clients become aware of these arrangements."</blockquote>

<h2>Client Impact</h2>
<p>Our analysis shows clients represented by Morrison & Associates:</p>
<ul>
<li>Paid interest rates 3-5% higher than market average</li>
<li>Accepted worse terms than comparable cases</li>
<li>Were steered exclusively to partner funding companies</li>
<li>Lost an estimated $45 million in excess costs</li>
</ul>

<p><em>[Article truncated - see full archive for complete investigation]</em></p>""",
        "status": "archived",
        "published_at": datetime.now() - timedelta(days=90)
    },
    {
        "title": "Bar Association's Cover-Up of Serial Sexual Harassment",
        "slug": "bar-association-coverup-sexual-harassment",
        "excerpt": "Documents show how a state bar association systematically ignored and covered up sexual harassment complaints against prominent attorneys for over a decade.",
        "content": """<p>ARCHIVED - This investigation led to significant reforms in bar association complaint procedures.</p>

<p>A cache of internal documents from the State Bar Association reveals a decade-long pattern of covering up sexual harassment complaints against well-connected attorneys, leaving victims without recourse and enabling serial predators to continue practicing.</p>

<h2>The System of Silence</h2>
<p>Between 2010 and 2020, the Bar received 147 sexual harassment complaints against attorneys. Our investigation found:</p>
<ul>
<li>89% of complaints were closed without investigation</li>
<li>Only 2 attorneys faced any disciplinary action</li>
<li>Multiple complaints against the same attorneys were ignored</li>
<li>Victims were discouraged from pursuing criminal charges</li>
</ul>

<p><em>[Article truncated - see full archive for complete investigation]</em></p>""",
        "status": "archived",
        "published_at": datetime.now() - timedelta(days=180)
    }
]

def get_auth_token():
    """Get authentication token"""
    response = requests.post(
        f"{API_BASE_URL}/api/auth/login",
        data={
            "username": ADMIN_USERNAME,
            "password": ADMIN_PASSWORD
        }
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Failed to authenticate: {response.status_code}")
        print(response.text)
        return None

def create_posts(token):
    """Create demo posts"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    created_count = 0
    
    for post_data in DEMO_POSTS:
        # Prepare the post data
        post_payload = {
            "title": post_data["title"],
            "slug": post_data["slug"],
            "excerpt": post_data["excerpt"],
            "content": post_data["content"],
            "status": post_data["status"]
        }
        
        # Create the post
        response = requests.post(
            f"{API_BASE_URL}/api/posts",
            headers=headers,
            json=post_payload
        )
        
        if response.status_code == 201:
            created_post = response.json()
            print(f"✓ Created post: {post_data['title']}")
            
            # If the post should be published and has a published_at date, update it
            if post_data["status"] == "published" and "published_at" in post_data:
                update_payload = {
                    "published_at": post_data["published_at"].isoformat()
                }
                update_response = requests.put(
                    f"{API_BASE_URL}/api/posts/{created_post['id']}",
                    headers=headers,
                    json=update_payload
                )
                if update_response.status_code == 200:
                    print(f"  → Set published date for post")
                else:
                    print(f"  → Failed to update published date: {update_response.status_code}")
            
            created_count += 1
        else:
            print(f"✗ Failed to create post: {post_data['title']}")
            print(f"  Error: {response.status_code} - {response.text}")
    
    return created_count

def main():
    print("=== LexLeaks Demo Posts Creator ===\n")
    
    print("Authenticating...")
    token = get_auth_token()
    
    if not token:
        print("Failed to authenticate. Make sure the backend is running and the admin user exists.")
        return
    
    print("Authentication successful!\n")
    
    print("Creating demo posts...")
    created = create_posts(token)
    
    print(f"\n=== Summary ===")
    print(f"Created {created} out of {len(DEMO_POSTS)} posts")
    print(f"Published posts: {len([p for p in DEMO_POSTS if p['status'] == 'published'])}")
    print(f"Archived posts: {len([p for p in DEMO_POSTS if p['status'] == 'archived'])}")
    
    print("\n✓ Demo content creation complete!")
    print("Visit http://localhost:3000 to see the posts")

if __name__ == "__main__":
    main() 