import openai


openai.api_type = "azure"
openai.api_base = "https://extractinfo.openai.azure.com/"
openai.api_version = "2023-07-01-preview"
openai.api_key = "30363b3002684528a6af160e7cb7ae31"


faq_data = {
    "What is OceanN Mail?": (
        "OceanN Mail (OM) is a cutting-edge, AI-enabled communication platform designed specifically for the maritime industry. "
        "Built to streamline email interactions across vast oceans, it ensures seamless, real-time connectivity between vessels, ports, "
        "and maritime professionals worldwide. With advanced features like route mapping, intelligent search, and a secure email system that adapts "
        "to the unique challenges of maritime communication, OceanN Mail empowers users to manage critical operations with confidence and precision. "
        "Whether you're coordinating logistics, responding to urgent inquiries, or managing fleet correspondence, OceanN Mail is the future of maritime "
        "communication—keeping you connected no matter where you are."
    ),
    "What is OceanN VM?": (
        "OceanN Voyage Manager (OVM) is a robust, all-in-one solution designed to optimize voyage planning and execution for maritime professionals. "
        "With advanced route optimization, real-time tracking, and intelligent reporting, OVM ensures smooth, efficient voyages from start to finish. "
        "Whether managing a single vessel or an entire fleet, OVM empowers users to streamline operations, reduce costs, and ensure compliance with "
        "industry regulations. Built to handle the complexities of global maritime logistics, OceanN Voyage Manager keeps your voyages on course and "
        "your operations running at peak performance."
    ),
    "How to reset my password in OceanN VM?": (
        "For OceanN Voyage Manager (OVM):\n"
        "1. Click 'Forgot Password' on the login page.\n"
        "2. Enter your registered email address.\n"
        "3. Check your inbox for the reset link, click it, and set a new password.\n"
        "Need help? Contact support anytime!"
    ),
    "How can I contact support?": (
        "Need help? For technical support contact:\n"
        "- Email: Jeetendra@theoceann.ai\n"
        "Customer Support:\n"
        "- Email: onboarding@theoceann.com\n"
        "Contact Support:\n"
        "- Email: astha@theoceann.ai\n"
        "Our team is waiting to resolve your queries."
    ),
    "What pricing plans are available?": "Contact our team to know more about our pricing plans and have a better understanding. “Click here to contact our Team”",
    "How to Track Your Voyages in OceanN Voyage Manager?": (
        "Simply log into OceanN Voyage Manager, head over to the 'Track Voyage' section, and get real-time updates on your fleet’s location, "
        "status, and route progress—all in one place!"
    ),
    "How does OceanN Mail handle email security?": (
        "OceanN Mail uses end-to-end encryption to safeguard your emails, ensuring your communication stays private. "
        "We also provide multi-factor authentication for added security. Key security features include:\n"
        "- SOC 2 Compliance\n"
        "- ISO 27001 Certification\n"
        "- NIST Cybersecurity Framework\n"
        "- GDPR Compliance\n"
        "- HIPAA Compliance\n"
        "- Single Sign-On (SSO) Integration\n"
        "- Data Encryption\n"
        "- Anti-Theft and Lock Features\n"
        "- Cloud Security Certifications\n"
        "- MongoDB Security\n"
        "- Regular Security Audits and Assessments\n"
        "- Multi-Factor Authentication (MFA)\n"
        "- Comprehensive Access Controls"
    ),
    "Can I schedule emails in OceanN Mail?": "Yes! OceanN Mail allows you to schedule emails to be sent at your preferred time.",
    "Can OceanN Voyage Manager optimize my route for fuel efficiency?": (
        "Yes! Our AI-driven route optimization feature helps you select the most fuel-efficient routes, cutting costs and reducing environmental impact "
        "while keeping your voyages on schedule."
    ),
    "How do I manage crew communication through OceanN Mail?": (
        "You can create dedicated email groups for your crew, set up priority notifications, and use tagging to categorize important messages—"
        "making crew communication smooth and organized."
    )
}



def generate_openai_response(prompt: str) -> str:
    try:
        response = openai.ChatCompletion.create(
            engine="gpt-4o",
            messages=[
                {"role": "system", "content": (
                    "You are OceannAI, a helpful assistant from TheOceann, which offers OM (Oceann Mail), OVM (Oceann Voyage Manager), "
                    "and OceannAI, all specialized in maritime products. "
                    "Respond to user queries in a well-structured HTML format with beautification, and CSS styling. "
                    "The response must include a summarized paragraph with the latest information. "
                    "The summary should be within 20 words and include a marketing strategy to attract the user. "
                    "Use paragraphs, bullet points, and spaces between sections for clarity. "
                    "If possible, add some action buttons to the response."
                    "Use headers with <h4> tags. "
                    "Use 'body1' as a class for body content. "
                    "Ensure the content is in 12px font size."
                )},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None
        )

        response_data = response['choices'][0]['message']['content']
        response_content = response_data.replace('```', '').strip()

        return response_content
    except Exception as e:
        print(f"An error occurred: {e}")
        return "Sorry, I couldn't process your request at the moment."


def get_chatbot_response(user_query: str) -> str:

    faq_answer = faq_data.get(user_query)

    if faq_answer:
        openai_prompt = (
            f"User asked: {user_query}\n"
            f"FAQ response: {faq_answer}\n"
            f"Generate a well-structured HTML response including this information."
        )
    else:
        openai_prompt = f"User: {user_query}\nAI:"

    return generate_openai_response(openai_prompt)
