from flask import Flask, jsonify, request, render_template, send_from_directory
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
import os
import urllib

app = Flask(__name__)

# Sample DataFrame
data = {
    'District': ['District1', 'District2', 'District1', 'District2'],
    'State': ['State1', 'State1', 'State2', 'State2'],
    'Month': ['January', 'February', 'March', 'April'],
    'Season': ['Winter', 'Winter', 'Spring', 'Spring'],
    'Crop1': ['WHEAT', 'Rice', 'Barley', 'Maize'],
    'Crop2': ['Corn', 'Wheat', 'Oats', 'Rice'],
    'Rainfall': [100, 150, 200, 250]
}
df = pd.DataFrame(data)

# Example sorted pairs data
sorted_pairs_seasons = pd.DataFrame({
    'Column Name': ['WHEAT', 'WHEAT', 'WHEAT', 'WHEAT'],
    'Season': ['Oct-Dec', 'Mar-May', 'Jun-Sep', 'Jan-Feb'],
    'Correlation': [-0.582526, -0.367133, -0.280149, 0.029938]
})

sorted_pairs_crops = pd.DataFrame({
    'Column Name': ['WHEAT']*27,
    'Crop': ['RAPESEED AND MUSTARD', 'BARLEY', 'FRUITS', 'FINGER MILLET', 'RABI SORGHUM', 
             'CHICKPEA', 'MAIZE', 'PEARL MILLET', 'PIGEONPEA', 'LINSEED', 
             'MINOR PULSES', 'POTATOES', 'FODDER', 'SAFFLOWER', 'SUNFLOWER', 
             'GROUNDNUT', 'SORGHUM', 'ONION', 'RICE', 'SUGARCANE', 'CASTOR', 
             'SESAMUM', 'KHARIF SORGHUM', 'COTTON', 'SOYABEAN', 'VEGETABLES', 
             'OILSEEDS'],
    'Correlation': [0.697734, 0.577132, -0.455622, -0.446333, -0.295990, 
                    0.285870, -0.231799, 0.229056, 0.206885, 0.173683, 
                    0.151290, 0.150121, 0.139388, -0.138866, -0.103962, 
                    -0.082805, -0.072365, -0.060503, -0.057967, 0.027976, 
                    0.019075, 0.016974, -0.013902, -0.007521, -0.002466, 
                    -0.002305, 0.000615]
})

subdivisions_to_districts = {
        "ANDAMAN & NICOBAR ISLANDS": ["North  & Middle Andaman", "South Andaman", "Nicobars"],

        "ARUNACHAL PRADESH": ["Tawang", "West Kameng", "East Kameng", "Papum Pare", "Lower Subansiri", "Kurung Kumey", "Upper Subansiri", "West Siang", "East Siang", "Upper Siang", "Lower Siang", "Siang", "Changlang", "Tirap", "Longding", "Namsai", "Lohit", "Anjaw", "Kra Daadi", "Kamle", "LOWER DIBANG VALLEY", "UPPER DIBANG VALLEY", "SHI YOM", "LEPA RADA", "PAKKE KESSANG" , ""],

        "ASSAM & MEGHALAYA": ["North Cachar Hil / Dima Hasao", "Sibsagar","Kamrup", "Nagaon", "Tinsukia", "Cachar", "Goalpara", "Hojai", "Ri-Bhoi", "East Khasi Hills", "West Khasi Hills", "South West Khasi Hills", "West Jaintia Hills", "East Jaintia Hills", "North Garo Hills", "East Garo Hills", "South Garo Hills", "South West Garo Hills", "WEST KARBI ANGLONG" , "BAKSA", "BARPETA", "LAKHIMPUR", "TINSUKIA", 
"KARBI ANGLONG","DHUBRI MAJULI","BISWANATH"," KOKRAJHAR",'CHARAIDEO','JORHAT','SOUTH SALMARA MANCACHAR','CHIRANG','KARIMGANJ','DIBRUGARH','SIVASAGAR','SONITPUR','DHEMAJI','DIMA HASAO','MORIGAON','KAMRUP METROPOLITAN','UDALGURI','NALBARI','BONGAIGAON','HAILAKANDI','GOLAGHAT','BAJALI','DARRANG'],

        "NAGA MANI MIZO TRIPURA": ["Kohima", "Dimapur", "Imphal", "Bishnupur", "Chandel", "Aizawl", "Gomati", "Dhalai", "Khowai", "North Tripura", "Sepahijala", "South Tripura", "Unakoti", "West Tripura"],

        "SUB HIMALAYAN WEST BENGAL & SIKKIM": ["Darjeeling", 'Cooch Behar', 'West Dinajpur', "Kalimpong", "Jalpaiguri", "East Sikkim", "West Sikkim", "North Sikkim", "South Sikkim"],

        "GANGETIC WEST BENGAL": ["Kolkata", "Howrah", "24 Parganas","Burdwan", "Malda", "Midnapur", "Hooghly", "Nadia", "Murshidabad", "Paschim Bardhaman", "Purba Bardhaman", "Birbhum", "Bankura", "Purulia"],

        "ORISSA": ["Phulbani ( Kandhamal )", "Balasore", "Bolangir", "Keonjhar", "Mayurbhanja", "Phulbani (Kandhamal)", "Sundargarh","Khordha", "Puri", "Cuttack", "Ganjam", "Balangir", "Kendujhar", "Bargarh", "Angul", "Boudh", "Bhadrak", "Debagarh", "Dhenkanal", "Gajapati", "Jagatsinghapur", "Jajpur", "Jharsuguda", "Kalahandi", "Kandhamal", "Koraput", "Malkangiri", "Mayurbhanj", "Nabarangpur", "Nayagarh", "Nuapada", "Rayagada", "Sambalpur", "Sonepur", "Sundergarh"],

        "JHARKHAND": ["Palamau", "Santhal Paragana / Dumka","Ranchi", "Jamshedpur", "Dhanbad", "Bokaro", "Deoghar", "Hazaribagh", "Giridih", "Ramgarh", "Palamu", "East Singhbhum", "West Singhbhum", "Singhbhum", "Chatra", "Garhwa", "Khunti", "Koderma", "Latehar", "Lohardaga", "Pakur", "Sahebganj", "Simdega", "Seraikela Kharsawan", 'SAHIBGANJ','GUMLA','GODDA','PURBI SINGHBHUM','PASHCHIMI SINGHBHUM','SARAIKELA-KHARSAWAN','KODARMA','JAMTARA','DUMKA'],
    
        "BIHAR": ["Champaran", "Mungair", "Purnea", "Shahabad (Now Part of Bhojpur District)","Patna", "Gaya", "Bhagalpur", "Muzaffarpur", "Darbhanga", "Bhojpur", "Begusarai", "Aurangabad", "Araria", "Arwal", "Banka", "Buxar", "East Champaran", "Jamui", "Jehanabad", "Kaimur", "Katihar", "Khagaria", "Kishanganj", "Lakhisarai", "Madhepura", "Madhubani", "Munger", "Nalanda", "Nawada", "Purnia", "Rohtas", "Saharsa", "Samastipur", "Saran", "Sheikhpura", "Sheohar", "Sitamarhi", "Siwan", "Supaul", "Vaishali", "West Champaran", 'PASHCHIM CHAMPARAN','PURBA CHAMPARAN','GOPALGANJ','KAIMUR (BHABUA)'],

        "EAST UTTAR PRADESH": ["Bahraich", "Banda", "Barabanki", "Buland Shahar", "Etah", "Etawah", "Faizabad", "Farrukhabad", "Fatehpur", "Ghazipur", "Gonda", "Hardoi", "Jalaun", "Jhansi", "Kanpur", "Kheri", "Lucknow", "Mainpuri", "Mirzpur", "Pilibhit", "Pratapgarh", "Rae-Bareily", "Saharanpur", "Sultanpur","Sitapur", "Unnao","Varanasi", "Allahabad", "Gorakhpur", "Azamgarh", "Jaunpur", "Ballia", "Basti", "Deoria", "Ghaziabad", "Maharajganj", "Mirzapur", "Sant Kabir Nagar", "Sant Ravidas Nagar", "Siddharthnagar"],

        "WEST UTTAR PRADESH": ["Ghaziabad", "Gautam Budh Nagar", "Baghpat", "Meerut", "Muzaffarnagar", "Shamli", "Saharanpur", "Bulandshahr", "Aligarh", "Mathura", "Hathras", "Agra", "Firozabad", "Mainpuri", "Etah", "Kasganj", "Meerut", "Agra", "Aligarh", "Ghaziabad", "Gautam Buddha Nagar", "Bulandshahr", "Hapur", "Mathura", "Firozabad", "Shamli", "Muzaffarnagar", "Bijnor", "Moradabad", "Sambhal", "Amroha", "Rampur", "Bareilly", "Budaun", "Shahjahanpur"],

        "UTTARAKHAND": ["Almorah", "Garhwal", "Pithorgarh", "Uttar Kashi","Dehradun", "Nainital", "Haridwar", "Almora", "Pauri Garhwal", "Pithoragarh", "Rudraprayag", "Tehri Garhwal", "Udham Singh Nagar", "Uttarkashi", "Chamoli", "Champawat"],

        "HARYANA DELHI & CHANDIGARH": ["Hissar", "Mahendragarh / Narnaul","Gurgaon", "Faridabad", "Central", "East", "North", "North East", "North West", "South", "South East", "South West", "West", "Chandigarh", "SHAHDARA", "NEW DELHI", 'NUH','MAHENDRAGARH','KURUKSHETRA','KARNAL','KAITHAL','JHAJJAR','HISAR','GURUGRAM','FATEHABAD','PALWAL','PALWAL','JIND','AMBALA','PANIPAT','REWARI','ROHTAK','PANCHKULA','SIRSA','CHARKI DADRI','YAMUNANAGAR','SONIPAT'],

        "PUNJAB": ["Bhatinda", "Ferozpur", "Roopnagar / Ropar","Amritsar", "Ludhiana", "Jalandhar", "Patiala", "Bathinda", "Mohali", "Gurdaspur", "Hoshiarpur", "Moga", "Kapurthala", "Sangrur", "Ferozepur", "Faridkot", "Rupnagar", "Pathankot", "Barnala", "Tarn Taran", "Fazilka", "SBS Nagar", "Mansa"],

        "HIMACHAL PRADESH": ["Bilashpur","Shimla", "Kangra", "Solan", "Mandi", "Kullu", "Una", "Hamirpur", "Chamba", "Bilaspur", "Sirmaur", "Kinnaur", "Lahul & Spiti"],

        "JAMMU & KASHMIR": ["Jammu", "Srinagar", "Anantnag", "Baramulla", "Udhampur", "Kathua", "Pulwama", "Kupwara", "Rajouri", "Doda", "Bandipora", "Shopian", "Ganderbal", "Kulgam", "Poonch", "Ramban", "Reasi", "Samba", 'BADGAM','KISHTWAR','SHUPIYAN','BARAMULA','BANDIPORE','PUNCH','MUZAFFARABAD','MIRPUR','KARGIL','LEH'],

        "WEST RAJASTHAN": ["Jodhpur", "Bikaner", "Barmer", "Jaisalmer", "Nagaur", "Churu", "Ganganagar", "Hanumangarh"],

        "EAST RAJASTHAN": ["Banswara", "Bhilwara", "Bundi", "Chittorgarh", "Dungarpur", "Jalore", "Jhunjhunu", "Pali", "Sikar", "Sirohi", "Swami Madhopur", "Udaipur","Jaipur", "Kota", "Alwar", "Bharatpur", "Ajmer", "Tonk", "Sawai Madhopur", "Dausa", "Jhalawar"],

        "WEST MADHYA PRADESH": ["Indore", "Ujjain", "Ratlam", "Dhar", "Dewas", "Khandwa", "Khargone", "Burhanpur",'MANDSAUR','GUNA','BETUL','VIDISHA','GWALIOR','RAJGARH','EAST NIMAR','DATIA','WEST NIMAR','RAISEN','BARWANI','BHIND','NEEMUCH','MORENA','ASHOKNAGAR'],

        "EAST MADHYA PRADESH": ["Balaghat", "Chhatarpur", "Damoh", "Jhabua", "Khandwa / East Nimar", "Khargone / West Nimar", "Mandla", "Narsinghpur", "Sagar", "Sehore", "Seoni / Shivani", "Shahdol", "Shajapur", "Shivpuri", "Sidhi", "Tikamgarh","Bhopal", "Jabalpur", "Rewa", "Satna", "Shahdol", "Singrauli", "Chhindwara", "Hoshangabad", "Narsimhapur", 'UMARIA','PANNA','NARSIMHAPUR','NIWARI','DINDORI'],

        "GUJARAT REGION": ["Banaskantha", "Dangs", "Mehsana", "Panchmahal", "Sabarkantha", "Vadodara / Baroda","Ahmedabad", "Surat", "Vadodara", "Gandhinagar", "Anand", "Navsari",  "Narmada", "DADRA & NAGAR HAVELI", "DAMAN",'MAHISAGAR','PANCH MAHALS','TAPI','PATAN','MAHESANA','KHEDA','SABAR KANTHA','DOHAD','BANAS KANTHAARAVALLI','VALSAD','NAVSARI','CHOTA UDAIPUR','BHARUCH','THE DANGS','AHMADABAD'],

        "SAURASHTRA & KUTCH": ["Kutch", "Jamnagar", "Kachchh", "Morbi", "Surendranagar", "Devbhumi Dwarka", 'DIU','GIR SOMNATH', "Porbandar","Jamnagar","Bhavnagar", "Rajkot", "Junagadh",  "Amreli", "Botad", "Morvi"],

        "KONKAN & GOA": ["Bombay", "Mumbai", "Thane", "Raigad", "Ratnagiri", "Sindhudurg", "North Goa", "South Goa"],

        "MADHYA MAHARASHTRA": ["Amarawati", "Dhule", "Nasik", "Solapur", "Yeotmal", "Pune", "Nashik", "Ahmednagar", "Satara", "Sangli", "Kolhapur", "Jalgaon"],

        "MATATHWADA": ["Aurangabad", "Jalna", "Beed", "Osmanabad", "Parbhani", "Latur", "Nanded", "Hingoli"],

        "VIDARBHA": ["Nagpur", "Amravati", "Chandrapur", "Bhandara", "Wardha", "Gondia", "Yavatmal", "Akola", "Washim", "Buldhana"],

        "CHHATTISGARH": ["Raipur", "Bilaspur", "Durg", "Bastar", "Dantewada", "Jashpur", "Kanker", "Kawardha", "Kondagaon", "Korba", "Koriya", "Mahasamund", "Mungeli", "Narayanpur", "Raigarh", "Rajnandgaon", "Sukma", "Surajpur", "Surguja", 'BAMETARA','BALODA BAZAR','BALOD','JANJGIR - CHAMPA','BALRAMPUR','KABEERDHAM','DHAMTARI','DAKSHIN BASTAR DANTEWADA','GAURELA-PENDRA-MARWAHI','UTTAR BASTAR KANKER','GARIABAND'],

        "COASTAL ANDHRA PRADESH": ["Visakhapatnam", "Krishna", "Guntur", "East Godavari", "West Godavari", "Srikakulam", "Vizianagaram", "Nellore", "Prakasam", "ALLURI SITHARAMA RAJU", "ANAKAPALLI", "BAPATLA", "PARVATHIPURAM MANYAM", "KAKINADA", "KONASEEMA", "SRI POTTI SRIRAMULU NELL*", "ELURU", "PALNADU", "NTR"],

        "TELANGANA": ["Hyderabad", "Warangal", "Nizamabad", "Karimnagar", "Khammam", "Mahabubnagar", "Ranga Reddy", "Medak", "Adilabad", "Nalgonda"],

        "RAYALSEEMA": ["Ananthapur", "Kadapa YSR", "S.P.S. Nellore","Kurnool", "Anantpur", "Chittoor", "Y.S.R.", "ANNAMAYYA", "NANDYAL", "SRI SATHYA SAI", "TIRUPATI"],

        "TAMIL NADU": ["Chengalpattu MGR / Kanchipuram", "Kanyakumari", "North Arcot / Vellore", "Ramananthapuram", "South Arcot / Cuddalore", "The Nilgiris", "Thirunelveli", "Tiruchirapalli / Trichy","Chennai", "Coimbatore", "Madurai", "Tiruchirappalli", "Salem", "Tirunelveli", "Vellore", "Thoothukudi", "Erode", "Cuddalore", "Kancheepuram", "Thanjavur", "Dindigul", "Krishnagiri", "Virudhunagar"],

        "COASTAL KARNATAKA": ["Dakshina Kannada", "Udupi", "Uttara Kannada"],

        "NORTH INTERIOR KARNATAKA": ["Bangalore", "Belgaum", "Bellary", "Bijapur / Vijayapura", "Chickmagalur", "Chitradurga", "Gulbarga / Kalaburagi", "Kodagu / Coorg", "Mysore", "Shimoge", "Tumkur","Dharwad", "Gadag", "Haveri", "Belagavi", "Bijapur", "Bagalkot", "Bidar", "Kalaburagi", "Koppal", "Raichur", "Yadgir",'BAGALKOTE','VIJAYAPURA'],

        "SOUTH INTERIOR KARNATAKA": ["Mysuru", "Mandya", "Hassan", "Chamarajanagara", "Bengaluru", "Ramanagara", "Tumakuru", "Chikkamagaluru", "Kodagu",'BALLARI','SHIVAMOGGA','VIJAYANAGAR','BENGALURU RURAL','CHIKKABALLAPURA','DAVANAGERE','BANGALORECHITRADURGA','KOLAR'],

        "KERALA": ["Eranakulam", "Thiruvananthapuram", "Ernakulam", "Kozhikode", "Kollam", "Thrissur", "Alappuzha", "Palakkad", "Malappuram", "Kottayam", "Kannur", "Wayanad", "Idukki", "Pathanamthitta", "Kasaragod"],

        "LAKSHADWEEP": ["LAKSHADWEEP"]
    }
    
def get_subdivision(district):
    for subdivision, districts in subdivisions_to_districts.items():
        districts = [div.upper() for div in districts]
        if district.upper() in districts:
            return subdivision.upper()
    return None

def get_districts(subdivision):    
    return [sub.upper() for sub in subdivisions_to_districts.get(subdivision, "Subdivision not found")]

districts_df = pd.read_csv(os.path.join("Database", 'districts.csv'))
seasons_df = pd.read_csv(os.path.join("Database", 'seasons.csv'))
crops_df = pd.read_csv(os.path.join("Database", 'crops.csv'))
IMAGE_DIRECTORY = 'Database/Forecasts'


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/forecasts/<path:subdiv>/<filename>')
def serve_image(subdiv, filename):
    # Make sure the path matches your actual folder structure
    return send_from_directory(os.path.join(IMAGE_DIRECTORY, subdiv), filename)

@app.route('/districts', methods=['GET'])
def get_districts():
    districts = districts_df['dtname'].unique().tolist()
    return jsonify(districts)

@app.route('/crops', methods=['GET'])
def get_crops():
    crops = seasons_df["Crop Name"].unique().tolist()
    return jsonify(crops)

@app.route('/crop_info', methods=['GET'])
def get_crop_info():
    district = request.args.get('district')
    crop = request.args.get('crop')

    if not district or not crop:
        return jsonify({"error": "Please provide both district and crop"}), 400

    with_seasons = seasons_df[seasons_df["Crop Name"] == crop.upper()]
    with_crops = crops_df[crops_df["Crop Name"] == crop.upper()]
    
    subdiv = get_subdivision(district)

    image_filenames = [
        'sarima_plot.png',
        'prophet_plot.png',
        'ets_plot.png',
        'lstm_plot.png'
    ]

    # Generate URLs for the plot images
    image_urls = {}
    for filename in image_filenames:
        image_path = os.path.join(IMAGE_DIRECTORY, subdiv, filename)
        encoded_filename = urllib.parse.quote(filename)

        if os.path.exists(image_path):
            image_urls[filename.split('.')[0]] = f'/forecasts/{urllib.parse.quote(subdiv)}/{encoded_filename}'
        else:
            image_urls[filename.split('.')[0]] = None
    
    response = {
        'season': with_seasons["Column Name"].to_list() if not with_seasons.empty else 'N/A',
        'crops': [c.title() for c in with_crops["Column Name"].to_list()][:5] if not with_crops.empty else 'N/A',
        'images': image_urls
    }

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)