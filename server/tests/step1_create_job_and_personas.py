import requests
import json
import os

PORTS = [8002]
BASE_URL = ""

def find_available_port():
    global BASE_URL
    for port in PORTS:
        try:
            url = f"http://localhost:{port}/health"
            print(f"  - Trying port {port}...")
            response = requests.get(url, timeout=1)
            if response.status_code == 200:
                BASE_URL = f"http://localhost:{port}/api/v1"
                print(f"✓ Server found on port {port}")
                return True
        except requests.exceptions.RequestException:
            continue
    return False

def main():
    print("--- Step 1: Create Job and Personas ---")

    print("\n[0/4] Finding available server port...")
    if not find_available_port():
        print("  ✗ Error: Could not find running server on port 8002.")
        return

    # 1. Create a test company
    print("\n[1/4] Creating a test company...")
    try:
        company_data = {"name": "삼성물산 패션부문 (Test)"}
        url = f"{BASE_URL}/companies/"
        print(f"  - Calling URL: {url}")
        response = requests.post(url, data=company_data)
        response.raise_for_status()
        company = response.json()
        company_id = company["id"]
        print(f"  ✓ Company created with ID: {company_id}")
    except requests.exceptions.RequestException as e:
        print(f"  ✗ Error creating company: {e}")
        print(f"  Response: {e.response.text}")
        return

    # 2. Upload JD and create a job
    print("\n[2/4] Uploading JD to create a job...")
    jd_pdf_path = "server/docs/jd.pdf"
    if not os.path.exists(jd_pdf_path):
        print(f"  ✗ Error: jd.pdf not found at {jd_pdf_path}")
        return

    job_data = {
        "company_id": str(company_id),
        "title": "상품기획(MD/MR) 및 Retail영업"
    }
    files = {
        "pdf_file": ("jd.pdf", open(jd_pdf_path, "rb"), "application/pdf")
    }

    try:
        response = requests.post(f"{BASE_URL}/jd-persona/upload", data=job_data, files=files)
        response.raise_for_status()
        job_analysis = response.json()
        job_id = job_analysis["job_id"]
        print(f"  ✓ Job created with ID: {job_id}")
        print(f"  - Analyzed Job Competencies: {job_analysis['job_competencies']}")
    except requests.exceptions.RequestException as e:
        print(f"  ✗ Error creating job: {e}")
        print(f"  Response: {e.response.text}")
        return

    # 3. Generate personas for the job
    print("\n[3/4] Generating personas for the job...")
    try:
        # Load questions from persona_data.json
        with open("server/assets/persona_data.json", "r", encoding="utf-8") as f:
            persona_data = json.load(f)
        company_questions = persona_data["initial_questions"]

        persona_request = {
            "job_id": job_id,
            "company_questions": company_questions
        }
        
        response = requests.post(f"{BASE_URL}/jd-persona/generate-persona", json=persona_request)
        response.raise_for_status()
        persona_response = response.json()
        print(f"  ✓ Personas generated successfully for Job ID: {job_id}")
        for i, summary in enumerate(persona_response["persona_summary"]):
            print(f"    - Persona {i+1}: {summary.get('name')} ({summary.get('role')})")

    except requests.exceptions.RequestException as e:
        print(f"  ✗ Error generating personas: {e}")
        print(f"  Response: {e.response.text}")
        return
        
    print("\n--- Step 1 successfully completed! ---")

if __name__ == "__main__":
    main()
