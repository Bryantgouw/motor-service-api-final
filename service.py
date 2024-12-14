import math
from typing import List
from geopy.distance import geodesic
from fastapi import FastAPI, Depends, HTTPException

from auth import AuthHandler
from schemas import AuthDetails

app = FastAPI()

# JWT AUTHENTICATION
users = []
authentication_handling = AuthHandler()

@app.post("/api/v1/auth/register", status_code=201)
def register(authentication_details: AuthDetails):
    if (any(x["username"] == authentication_details.username for x in users)):
        raise HTTPException(status_code=400, detail='Username is not available, please input other username')
    
    hashing_password = authentication_handling.get_hashing_password(authentication_details.password)
    
    users.append({
        "username" : authentication_details.username,
        "password" : hashing_password    
    })

    return

@app.post("/api/v1/auth/login")
def login(authentication_details: AuthDetails):
    user = None
    for x in users:
        if (x["username"] == authentication_details.username) :
            user = x
            break
    
    if ((not authentication_handling.password_verification(authentication_details.password, user['password'])) or (user is None)):
        raise HTTPException(status_code=401, detail='Invalid username or password')
    
    jwt_token = authentication_handling.encode_jwt_token(user['username'])
    return { "jwt_token" : jwt_token }

@app.get("/api/v1/auth/unprotected")
def unprotected():
    return { "default" : "screen" }

@app.get("/api/v1/auth/protected")
def protected(username=Depends(authentication_handling.authentication_wrapper)):
    return { "username": username }


# API MOTORCYCLE EMERGENCY SERVICES COMPANY
@app.get("/api/v1")
async def root(username: str = Depends(authentication_handling.authentication_wrapper)):
    return{"Message" : "Welcome to the Motorcycle Emergency Service Company API v1 !"}

@app.get("/api/v1/service-locations/{loc_id}")
async def get_service_location(loc_id: int, username: str = Depends(authentication_handling.authentication_wrapper)):
    if (loc_id == 1) :
        return {
            "Service Location id" : 1,
            "Nama Tempat" : "Cahaya Motors Service",
            "Alamat" : "Jl. Puri Kencana 24, Kebon Rawan Malink",
            "Kota" : "Jakarta Pusat",
            "Ketersediaan Servis" : "Perbaikan Umum, Ganti Oli, Tambal Ban, Ganti Aki",
            "Kode Servis" : 2,
            "Nomor Telepon" : "(+62)85628917",
            "Waktu Buka" : "7 Pagi",
            "Waktu Tutup" : "11 Malam"
            }
    elif (loc_id == 2) :
        return {
            "Service Location id" : 2,
            "Nama Tempat" : "Bengkel Citra Bahari",
            "Alamat" : "Jl. Sultan Wisma Kembangan 45, Kawah Kecil",
            "Kota" : "Jakarta Selatan",
            "Ketersediaan Servis" : "Perbaikan Umum, Tambal Ban, Ganti Aki",
            "Kode Servis" : 1,
            "Nomor Telepon" : "(+62)81342143",
            "Waktu Buka" : "8 Pagi",
            "Waktu Tutup" : "12 Malam"
            }
    elif (loc_id == 3) :
        return {
            "Service Location id" : 3,
            "Nama Tempat" : "Wijaya Services",
            "Alamat" : "Jl. Prapatan Surapati 13, Minggir Gebang",
            "Kota" : "Jakarta Barat",
            "Ketersediaan Servis" : "Perbaikan Umum",
            "Kode Servis" : 2,
            "Nomor Telepon" : "(+62)81342143",
            "Waktu Buka" : "10 Pagi",
            "Waktu Tutup" : "10 Malam"
            }
    else:
        raise HTTPException(status_code=404, detail="Service Location tidak ditemukan")
    
@app.get("/api/v1/ongkir-fee-calculation")
async def ongkir_fee_calculation(distance: float, vehicle_type: str, username: str = Depends(authentication_handling.authentication_wrapper)):
    if (vehicle_type not in ["motor", "truk"]):
        raise HTTPException(status_code=400, detail="Vehicle type invalid. diharapkan untuk menginput 'motor' atau 'truk'.")
    
    if (vehicle_type == "motor"):
        harga_per_km = 2000
    elif (vehicle_type == "truk"):
        harga_per_km = 3000
    
    calculation = math.ceil(distance * harga_per_km)
    return {
        "Distance" : distance,
        "Tipe Kendaraan" : vehicle_type,
        "Biaya Ongkir" : calculation
    }

services = {
    "perbaikan_umum_ringan": 75000,
    "perbaikan_umum_sedang": 150000,
    "perbaikan_umum_berat": 300000,
    "ganti_aki": 50000, 
    "ganti_oli": 30000, 
    "tambal_ban": 20000
}

@app.get("/api/v1/service-fee-calculation")
async def service_fee_calculation(service_digunakan: List[str], biaya_tambahan: int, username: str = Depends(authentication_handling.authentication_wrapper)):
    fee_total = 0
    fee_servis = 0
    services_tidak_valid = []

    for service in service_digunakan:
        if (service in services):
            fee_total = fee_total + services[service]
            fee_servis = fee_servis + services[service]
        else:
            services_tidak_valid.append(service)

    if (services_tidak_valid):
        raise HTTPException(status_code=400, detail=f"Invalid tipe services : {', '.join(services_tidak_valid)}")

    if (biaya_tambahan > 0) : 
        fee_total = fee_total + biaya_tambahan

    return {
        "service_digunakan": service_digunakan,
        "biaya_servis": fee_servis,
        "biaya_tambahan": biaya_tambahan,
        "total_biaya": fee_total
    }

service_locations = [
    {"nama_tempat": "Cahaya Motors Service", "latitude": 6.180500, "longitude": 106.828400}, #Jakarta Pusat
    {"nama_tempat": "Bengkel Citra Bahari", "latitude": 6.261500, "longitude": 106.810600}, #Jakarta Selatan
    {"nama_tempat": "Wijaya Services", "latitude": 6.167400, "longitude": 106.763700} #Jakarta Barat
]

@app.get("/api/v1/nearest-store")
def get_nearest_store(user_latitude: float, user_longitude: float, username: str = Depends(authentication_handling.authentication_wrapper)):
    if (not service_locations):
        raise HTTPException(status_code=404, detail="No service-locations available.")

    user_loc = (user_latitude, user_longitude)
    the_nearest = min(service_locations, key=lambda r: geodesic(user_loc, (r["latitude"], r["longitude"])).kilometers,)
    total_distance = geodesic(user_loc, (the_nearest["latitude"], the_nearest["longitude"])).kilometers

    return {
        "tempat_terdekat": the_nearest["nama_tempat"],
        "koordinat": {
            "latitude": the_nearest["latitude"],
            "longitude": the_nearest["longitude"],
        },
        "total_jarak_km": round(total_distance, 4),
    }