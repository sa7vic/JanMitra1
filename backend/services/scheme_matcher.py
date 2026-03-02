from models.database import db, Scheme, User, UserScheme
import json

class SchemeMatcher:
    def __init__(self, app=None):
        self.app = app
        if app:
            with app.app_context():
                self._ensure_schemes_loaded()
    
    def _ensure_schemes_loaded(self):
        if Scheme.query.count() == 0:
            self._load_comprehensive_schemes()
    
    def _load_comprehensive_schemes(self):
        schemes_data = [
            {
                'name': 'Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)',
                'short_name': 'PM-KISAN',
                'description': 'Direct income support of ₹6,000 per year to all farmer families across the country in three equal installments',
                'category': 'agriculture',
                'eligibility_criteria': json.dumps({
                    'occupation': ['farmer', 'agriculture'],
                    'land_ownership': True,
                    'income_limit': None,
                    'family_criteria': 'land owning farmer families'
                }),
                'benefits': '₹2,000 every 4 months directly to bank account (₹6,000/year)',
                'documents_required': json.dumps([
                    'Aadhaar Card',
                    'Bank Account Details',
                    'Land Ownership Documents'
                ]),
                'how_to_apply': 'Visit pmkisan.gov.in and register with Aadhaar number or visit nearest Common Service Centre',
                'application_process': json.dumps([
                    'Visit PM-KISAN portal',
                    'Click on Farmers Corner > New Farmer Registration',
                    'Enter Aadhaar number and state',
                    'Fill registration form with bank details',
                    'Submit land records',
                    'Receive registration number'
                ]),
                'url': 'https://pmkisan.gov.in',
                'ministry': 'Ministry of Agriculture & Farmers Welfare',
                'target_beneficiaries': 110000000,
                'budget_allocated': 60000.0,
                'active': True,
                'priority': 10
            },
            {
                'name': 'Ayushman Bharat - Pradhan Mantri Jan Arogya Yojana (PM-JAY)',
                'short_name': 'Ayushman Bharat',
                'description': 'World\'s largest health insurance scheme providing coverage of ₹5 lakh per family per year for secondary and tertiary care hospitalization',
                'category': 'health',
                'eligibility_criteria': json.dumps({
                    'annual_income': 500000,
                    'income_condition': 'below',
                    'automatic_inclusion': 'SECC 2011 beneficiaries',
                    'family_size': None
                }),
                'benefits': 'Free health insurance coverage up to ₹5 lakh per family per year for hospitalization',
                'documents_required': json.dumps([
                    'Aadhaar Card',
                    'Ration Card',
                    'Income Certificate (if required)'
                ]),
                'how_to_apply': 'Check eligibility at pmjay.gov.in or visit empanelled hospital with Aadhaar for instant enrollment',
                'application_process': json.dumps([
                    'Visit pmjay.gov.in',
                    'Check eligibility with mobile number',
                    'If eligible, visit nearest empanelled hospital',
                    'Provide Aadhaar for verification',
                    'Receive Ayushman card',
                    'Avail cashless treatment'
                ]),
                'url': 'https://pmjay.gov.in',
                'ministry': 'Ministry of Health and Family Welfare',
                'target_beneficiaries': 500000000,
                'budget_allocated': 6400.0,
                'active': True,
                'priority': 10
            },
            {
                'name': 'National Scholarship Portal',
                'short_name': 'NSP',
                'description': 'One-stop solution for various scholarship schemes for students belonging to different categories',
                'category': 'education',
                'eligibility_criteria': json.dumps({
                    'occupation': ['student'],
                    'annual_income': 800000,
                    'income_condition': 'below',
                    'education_level': ['higher_secondary', 'graduation', 'post_graduation'],
                    'age_range': [16, 35]
                }),
                'benefits': 'Scholarships ranging from ₹10,000 to ₹50,000 per year depending on category and course',
                'documents_required': json.dumps([
                    'Aadhaar Card',
                    'Bank Account Details',
                    'Income Certificate',
                    'Previous Year Marksheet',
                    'Current Year Admission Receipt',
                    'Category Certificate (if applicable)'
                ]),
                'how_to_apply': 'Register on scholarships.gov.in during application period and submit required documents',
                'application_process': json.dumps([
                    'Visit scholarships.gov.in',
                    'Register with basic details',
                    'Login and fill application form',
                    'Upload required documents',
                    'Submit application',
                    'Track status on portal'
                ]),
                'url': 'https://scholarships.gov.in',
                'ministry': 'Ministry of Education',
                'target_beneficiaries': 10000000,
                'budget_allocated': 5000.0,
                'active': True,
                'priority': 9
            },
            {
                'name': 'Pradhan Mantri Mudra Yojana (PMMY)',
                'short_name': 'Mudra Loan',
                'description': 'Provides loans up to ₹10 lakh to non-corporate, non-farm small/micro enterprises',
                'category': 'business',
                'eligibility_criteria': json.dumps({
                    'occupation': ['business', 'entrepreneur', 'self_employed'],
                    'business_type': ['manufacturing', 'trading', 'services'],
                    'existing_business': False
                }),
                'benefits': 'Collateral-free loans: Shishu (up to ₹50,000), Kishore (₹50,001-₹5 lakh), Tarun (₹5-₹10 lakh)',
                'documents_required': json.dumps([
                    'Identity Proof (Aadhaar/PAN)',
                    'Address Proof',
                    'Business Plan/Proposal',
                    'Bank Statements (6 months)',
                    'Business Registration (if any)',
                    'Quotation of equipment/machinery'
                ]),
                'how_to_apply': 'Apply through any bank or NBFC offering MUDRA loans with business plan',
                'application_process': json.dumps([
                    'Prepare business plan',
                    'Visit nearest bank/NBFC',
                    'Fill Mudra loan application',
                    'Submit required documents',
                    'Loan assessment by bank',
                    'Approval and disbursement'
                ]),
                'url': 'https://www.mudra.org.in',
                'ministry': 'Ministry of Finance',
                'target_beneficiaries': 50000000,
                'budget_allocated': 350000.0,
                'active': True,
                'priority': 8
            },
            {
                'name': 'Pradhan Mantri Kaushal Vikas Yojana (PMKVY)',
                'short_name': 'PMKVY',
                'description': 'Skill development scheme providing free training and certification to youth',
                'category': 'skill_development',
                'eligibility_criteria': json.dumps({
                    'age_range': [15, 45],
                    'education_level': ['10th_pass', 'any'],
                    'occupation': ['student', 'unemployed', 'job_seeker']
                }),
                'benefits': 'Free skill training, assessment, certification, and monetary reward on completion',
                'documents_required': json.dumps([
                    'Aadhaar Card',
                    'Bank Account Details',
                    'Educational Certificates'
                ]),
                'how_to_apply': 'Register on pmkvyofficial.org or visit nearest training center',
                'application_process': json.dumps([
                    'Visit pmkvyofficial.org',
                    'Find training center near you',
                    'Enroll in desired course',
                    'Complete training program',
                    'Appear for assessment',
                    'Receive certificate and monetary reward'
                ]),
                'url': 'https://www.pmkvyofficial.org',
                'ministry': 'Ministry of Skill Development & Entrepreneurship',
                'target_beneficiaries': 10000000,
                'budget_allocated': 3000.0,
                'active': True,
                'priority': 8
            },
            {
                'name': 'Pradhan Mantri Awas Yojana (PMAY-Urban)',
                'short_name': 'PMAY-Urban',
                'description': 'Housing for all scheme providing interest subsidy and assistance for affordable housing',
                'category': 'housing',
                'eligibility_criteria': json.dumps({
                    'annual_income': 1800000,
                    'income_condition': 'below',
                    'home_ownership': False,
                    'family_criteria': 'should not own pucca house anywhere in India'
                }),
                'benefits': 'Interest subsidy up to ₹2.67 lakh on home loans or direct assistance of ₹1.5 lakh',
                'documents_required': json.dumps([
                    'Aadhaar Card',
                    'Income Certificate',
                    'Bank Account Details',
                    'Affidavit stating no house ownership',
                    'Sale Agreement/Allotment Letter'
                ]),
                'how_to_apply': 'Apply through pmaymis.gov.in or through bank for credit-linked subsidy',
                'application_process': json.dumps([
                    'Visit pmaymis.gov.in',
                    'Select applicable scheme component',
                    'Fill online application',
                    'Upload required documents',
                    'Submit to ULB for verification',
                    'Receive approval and subsidy'
                ]),
                'url': 'https://pmaymis.gov.in',
                'ministry': 'Ministry of Housing and Urban Affairs',
                'target_beneficiaries': 20000000,
                'budget_allocated': 50000.0,
                'active': True,
                'priority': 9
            },
            {
                'name': 'Stand Up India Scheme',
                'short_name': 'Stand Up India',
                'description': 'Facilitates bank loans between ₹10 lakh to ₹1 crore for SC/ST and women entrepreneurs',
                'category': 'entrepreneurship',
                'eligibility_criteria': json.dumps({
                    'gender': ['female'],
                    'category': ['SC', 'ST'],
                    'age_range': [18, 65],
                    'occupation': ['entrepreneur', 'business'],
                    'business_type': ['new', 'greenfield']
                }),
                'benefits': 'Loans between ₹10 lakh to ₹1 crore for setting up greenfield enterprise',
                'documents_required': json.dumps([
                    'Aadhaar Card',
                    'PAN Card',
                    'Caste Certificate (for SC/ST)',
                    'Business Plan',
                    'Project Report',
                    'Address Proof'
                ]),
                'how_to_apply': 'Apply online through standupmitra.in or approach bank directly',
                'application_process': json.dumps([
                    'Visit standupmitra.in',
                    'Register as borrower',
                    'Fill loan application',
                    'Upload business plan',
                    'Submit to selected bank',
                    'Bank appraisal and approval',
                    'Loan disbursement in phases'
                ]),
                'url': 'https://www.standupmitra.in',
                'ministry': 'Ministry of Finance',
                'target_beneficiaries': 250000,
                'budget_allocated': 10000.0,
                'active': True,
                'priority': 7
            },
            {
                'name': 'Pradhan Mantri Fasal Bima Yojana (PMFBY)',
                'short_name': 'Crop Insurance',
                'description': 'Comprehensive crop insurance against all non-preventable natural risks',
                'category': 'agriculture',
                'eligibility_criteria': json.dumps({
                    'occupation': ['farmer', 'agriculture'],
                    'land_ownership': None,
                    'crops': ['all notified crops']
                }),
                'benefits': 'Insurance coverage against crop loss due to natural calamities, pests, diseases',
                'documents_required': json.dumps([
                    'Aadhaar Card',
                    'Bank Account Details',
                    'Land Records',
                    'Sowing Certificate'
                ]),
                'how_to_apply': 'Apply through bank, CSC, or pmfby.gov.in within cutoff date after sowing',
                'application_process': json.dumps([
                    'Visit pmfby.gov.in or bank',
                    'Select crop and area',
                    'Pay premium (2% for Kharif, 1.5% for Rabi)',
                    'Submit required documents',
                    'Receive insurance certificate',
                    'Claim in case of crop loss'
                ]),
                'url': 'https://pmfby.gov.in',
                'ministry': 'Ministry of Agriculture & Farmers Welfare',
                'target_beneficiaries': 50000000,
                'budget_allocated': 15000.0,
                'active': True,
                'priority': 9
            },
            {
                'name': 'National Pension System (NPS)',
                'short_name': 'NPS',
                'description': 'Voluntary retirement savings scheme for building retirement corpus',
                'category': 'pension',
                'eligibility_criteria': json.dumps({
                    'age_range': [18, 70],
                    'citizenship': 'Indian',
                    'kyc_required': True
                }),
                'benefits': 'Tax benefits u/s 80C (₹1.5L) + 80CCD(1B) (₹50K), market-linked returns, pension on retirement',
                'documents_required': json.dumps([
                    'Aadhaar Card',
                    'PAN Card',
                    'Bank Account Details',
                    'Address Proof',
                    'Photograph'
                ]),
                'how_to_apply': 'Register through enps.nsdl.com or visit Point of Presence (Bank/Post Office)',
                'application_process': json.dumps([
                    'Visit enps.nsdl.com',
                    'Click on Registration',
                    'Fill subscriber registration form',
                    'Complete e-KYC with Aadhaar',
                    'Receive PRAN (Permanent Retirement Account Number)',
                    'Start contributing'
                ]),
                'url': 'https://enps.nsdl.com',
                'ministry': 'Ministry of Finance',
                'target_beneficiaries': 50000000,
                'budget_allocated': 5000.0,
                'active': True,
                'priority': 6
            },
            {
                'name': 'Pradhan Mantri Jan Dhan Yojana (PMJDY)',
                'short_name': 'Jan Dhan Account',
                'description': 'Financial inclusion program for comprehensive access to banking facilities',
                'category': 'financial_inclusion',
                'eligibility_criteria': json.dumps({
                    'age_range': [10, 100],
                    'citizenship': 'Indian',
                    'existing_account': False
                }),
                'benefits': 'Zero balance account, RuPay debit card, ₹10,000 overdraft facility, accident insurance',
                'documents_required': json.dumps([
                    'Aadhaar Card (preferred)',
                    'or Voter ID/Driving License',
                    'Photograph'
                ]),
                'how_to_apply': 'Visit any bank branch with Aadhaar card',
                'application_process': json.dumps([
                    'Visit nearest bank branch',
                    'Request for Jan Dhan account',
                    'Fill simple application form',
                    'Provide Aadhaar for e-KYC',
                    'Receive account number instantly',
                    'Get RuPay card in 7-10 days'
                ]),
                'url': 'https://pmjdy.gov.in',
                'ministry': 'Ministry of Finance',
                'target_beneficiaries': 500000000,
                'budget_allocated': 3000.0,
                'active': True,
                'priority': 10
            },
            {
                'name': 'Atal Pension Yojana (APY)',
                'short_name': 'APY',
                'description': 'Pension scheme for unorganized sector workers providing guaranteed pension',
                'category': 'pension',
                'eligibility_criteria': json.dumps({
                    'age_range': [18, 40],
                    'occupation': ['unorganized_sector', 'self_employed', 'worker'],
                    'account_required': 'savings bank or post office'
                }),
                'benefits': 'Guaranteed pension of ₹1,000 to ₹5,000 per month after age 60',
                'documents_required': json.dumps([
                    'Aadhaar Card',
                    'Bank Account Details',
                    'Mobile Number'
                ]),
                'how_to_apply': 'Enroll through bank or post office where you have savings account',
                'application_process': json.dumps([
                    'Visit your bank/post office',
                    'Fill APY registration form',
                    'Provide Aadhaar and consent',
                    'Select pension amount (₹1K-₹5K)',
                    'Auto-debit setup for contributions',
                    'Receive APY PRAN'
                ]),
                'url': 'https://npscra.nsdl.co.in/apy',
                'ministry': 'Ministry of Finance',
                'target_beneficiaries': 50000000,
                'budget_allocated': 2000.0,
                'active': True,
                'priority': 7
            },
            {
                'name': 'Pradhan Mantri Suraksha Bima Yojana (PMSBY)',
                'short_name': 'PMSBY',
                'description': 'Accidental death and disability insurance at nominal premium',
                'category': 'insurance',
                'eligibility_criteria': json.dumps({
                    'age_range': [18, 70],
                    'account_required': 'savings bank account',
                    'premium': 12
                }),
                'benefits': '₹2 lakh coverage for accidental death or permanent total disability, ₹1 lakh for partial disability',
                'documents_required': json.dumps([
                    'Savings Bank Account',
                    'Aadhaar Card',
                    'Consent for auto-debit'
                ]),
                'how_to_apply': 'Enroll through bank by submitting consent form for ₹12/year premium auto-debit',
                'application_process': json.dumps([
                    'Visit your bank branch',
                    'Fill PMSBY enrollment form',
                    'Provide consent for ₹12 annual deduction',
                    'Submit Aadhaar details',
                    'Enrollment confirmed',
                    'Coverage starts immediately'
                ]),
                'url': 'https://www.jansuraksha.gov.in',
                'ministry': 'Ministry of Finance',
                'target_beneficiaries': 300000000,
                'budget_allocated': 500.0,
                'active': True,
                'priority': 8
            },
            {
                'name': 'Pradhan Mantri Jeevan Jyoti Bima Yojana (PMJJBY)',
                'short_name': 'PMJJBY',
                'description': 'Life insurance cover of ₹2 lakh at affordable premium',
                'category': 'insurance',
                'eligibility_criteria': json.dumps({
                    'age_range': [18, 50],
                    'account_required': 'savings bank account',
                    'premium': 436
                }),
                'benefits': '₹2 lakh life insurance coverage for any reason of death',
                'documents_required': json.dumps([
                    'Savings Bank Account',
                    'Aadhaar Card',
                    'Consent for auto-debit'
                ]),
                'how_to_apply': 'Enroll through bank by submitting consent for ₹436/year premium auto-debit',
                'application_process': json.dumps([
                    'Visit your bank branch',
                    'Fill PMJJBY enrollment form',
                    'Provide consent for ₹436 annual deduction',
                    'Submit Aadhaar details',
                    'Nomination details',
                    'Coverage starts next day'
                ]),
                'url': 'https://www.jansuraksha.gov.in',
                'ministry': 'Ministry of Finance',
                'target_beneficiaries': 200000000,
                'budget_allocated': 1000.0,
                'active': True,
                'priority': 8
            },
            {
                'name': 'Sukanya Samriddhi Yojana (SSY)',
                'short_name': 'SSY',
                'description': 'Savings scheme for girl child with attractive interest rate and tax benefits',
                'category': 'savings',
                'eligibility_criteria': json.dumps({
                    'gender': ['female'],
                    'age_range': [0, 10],
                    'max_accounts': 2,
                    'citizenship': 'Indian'
                }),
                'benefits': 'High interest rate (currently 8.2%), tax benefits u/s 80C, maturity at 21 years',
                'documents_required': json.dumps([
                    'Birth Certificate of Girl Child',
                    'Aadhaar of Parent/Guardian',
                    'Address Proof',
                    'Photograph of Parent and Child'
                ]),
                'how_to_apply': 'Open account at post office or authorized bank with minimum ₹250',
                'application_process': json.dumps([
                    'Visit post office or authorized bank',
                    'Fill SSY account opening form',
                    'Submit required documents',
                    'Deposit minimum ₹250',
                    'Receive passbook',
                    'Continue deposits (min ₹250, max ₹1.5L per year)'
                ]),
                'url': 'https://www.nsiindia.gov.in',
                'ministry': 'Ministry of Finance',
                'target_beneficiaries': 20000000,
                'budget_allocated': 2000.0,
                'active': True,
                'priority': 9
            },
            {
                'name': 'Soil Health Card Scheme',
                'short_name': 'Soil Health Card',
                'description': 'Provides soil test-based nutrient recommendations to farmers',
                'category': 'agriculture',
                'eligibility_criteria': json.dumps({
                    'occupation': ['farmer', 'agriculture'],
                    'land_ownership': None
                }),
                'benefits': 'Free soil testing and customized fertilizer recommendations to improve productivity',
                'documents_required': json.dumps([
                    'Land Records',
                    'Aadhaar Card',
                    'Soil Sample'
                ]),
                'how_to_apply': 'Contact local agriculture office or visit soilhealth.dac.gov.in',
                'application_process': json.dumps([
                    'Visit local agriculture office',
                    'Register for soil testing',
                    'Provide soil sample from field',
                    'Receive Soil Health Card in 15 days',
                    'Get customized fertilizer recommendations',
                    'Renew every 2 years'
                ]),
                'url': 'https://soilhealth.dac.gov.in',
                'ministry': 'Ministry of Agriculture & Farmers Welfare',
                'target_beneficiaries': 140000000,
                'budget_allocated': 500.0,
                'active': True,
                'priority': 7
            }
        ]
        
        for scheme_data in schemes_data:
            scheme = Scheme(**scheme_data)
            db.session.add(scheme)
        
        db.session.commit()
        print(f"✅ Loaded {len(schemes_data)} comprehensive schemes")
    
    def match_schemes_for_user(self, user_id):
        user = User.query.get(user_id)
        if not user:
            return []
        
        all_schemes = Scheme.query.filter_by(active=True).all()
        matched_schemes = []
        
        for scheme in all_schemes:
            score = self._calculate_match_score(user, scheme)
            if score > 0:
                user_scheme = UserScheme.query.filter_by(
                    user_id=user_id,
                    scheme_id=scheme.id
                ).first()
                
                if not user_scheme:
                    user_scheme = UserScheme(
                        user_id=user_id,
                        scheme_id=scheme.id,
                        status='eligible',
                        match_score=score
                    )
                    db.session.add(user_scheme)
                else:
                    user_scheme.match_score = score
                
                matched_schemes.append({
                    'scheme': scheme.to_dict(),
                    'match_score': score,
                    'user_scheme': user_scheme.to_dict()
                })
        
        db.session.commit()
        
        matched_schemes.sort(key=lambda x: x['match_score'], reverse=True)
        return matched_schemes
    
    def _calculate_match_score(self, user, scheme):
        score = 0
        criteria = json.loads(scheme.eligibility_criteria) if scheme.eligibility_criteria else {}
        
        if criteria.get('occupation'):
            allowed_occupations = criteria['occupation']
            if user.occupation and any(occ in user.occupation.lower() for occ in allowed_occupations):
                score += 30
        
        if criteria.get('annual_income'):
            income_limit = criteria['annual_income']
            condition = criteria.get('income_condition', 'below')
            if user.annual_income:
                if condition == 'below' and user.annual_income < income_limit:
                    score += 25
                elif condition == 'above' and user.annual_income > income_limit:
                    score += 25
        
        if criteria.get('age_range'):
            min_age, max_age = criteria['age_range']
            if user.age and min_age <= user.age <= max_age:
                score += 20
        
        if criteria.get('gender'):
            allowed_genders = criteria['gender']
            if user.gender and user.gender.lower() in [g.lower() for g in allowed_genders]:
                score += 15
        
        if criteria.get('land_ownership') is not None:
            if user.land_ownership == criteria['land_ownership']:
                score += 15
        
        if criteria.get('education_level'):
            allowed_levels = criteria['education_level']
            if user.education and any(level in user.education.lower() for level in allowed_levels):
                score += 10
        
        if scheme.category in ['health', 'insurance', 'financial_inclusion']:
            score += 5
        
        if user.state and scheme.name:
            score += 3
        
        return min(score, 100)
    
    def get_enrolled_schemes(self, user_id):
        user_schemes = UserScheme.query.filter_by(
            user_id=user_id,
            status='enrolled'
        ).all()
        
        return [us.to_dict() for us in user_schemes]
    
    def get_eligible_schemes(self, user_id):
        user_schemes = UserScheme.query.filter_by(
            user_id=user_id,
            status='eligible'
        ).order_by(UserScheme.match_score.desc()).all()
        
        return [us.to_dict() for us in user_schemes]
