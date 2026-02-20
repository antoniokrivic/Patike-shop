# Patike Shop — kratke upute za pokretanje 

Ovo su najvažniji koraci da projekt radi na novom ili postojećem računalu.

## Preduvjeti

- **Git**: https://git-scm.com/downloads
- **Python 3.10+** (tijekom instalacije označiti *Add Python to PATH*)
- **Node.js (LTS)** (dolazi s `npm`): https://nodejs.org/

Brza provjera:

```bash
git --version
python --version
node --version
npm --version
```

## 1) Postavljanje projekta (prvi put)

U Git Bashu uđite u folder projekta (primjer za vaš PC):

```bash
cd /c/Users/Antonio/Desktop/Antonio/Webshop/Webshop/patike-shop
```

Ako tek klonirate repozitorij:

```bash
cd /c/Users/YourUsername/Desktop
git clone https://github.com/antoniokrivic/Webshop.git
cd Webshop/Webshop/patike-shop
```

### Python (Django)

```bash
python -m venv venv
source venv/Scripts/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Node (Tailwind)

```bash
npm install
```

### Baza (SQLite lokalno)

```bash
python manage.py migrate
python manage.py createsuperuser
```

Opcionalno (testni podaci):

```bash
python manage.py seed_products
python manage.py populate_descriptions
```

## 2) Pokretanje (svaki put)

Otvorite **dva** Git Bash prozora.

### Terminal 1 — Django server

```bash
cd /c/Users/Antonio/Desktop/Antonio/Webshop/Webshop/patike-shop
source venv/Scripts/activate
python manage.py runserver
```

Stranica: http://127.0.0.1:8000  
Admin: http://127.0.0.1:8000/admin

### Terminal 2 — Tailwind (watch)

```bash
cd /c/Users/Antonio/Desktop/Antonio/Webshop/Webshop/patike-shop
npm run watch:css
```

Ako ne mijenjate CSS, možete umjesto watch-a samo jednom izgraditi CSS:

```bash
npm run build:css
```

## Najčešći problemi (brzo)

- **`python` nije prepoznat**: reinstalirati Python i označiti *Add Python to PATH*.
- **`npm` nije prepoznat**: instalirati Node.js (LTS), zatvoriti i ponovno otvoriti Git Bash.
- **Port 8000 je zauzet**:

```bash
python manage.py runserver 8080
```

- **Ne učitava se CSS**: pokrenuti `npm run watch:css` ili barem `npm run build:css`.

## Korisno

```bash
pytest
python manage.py makemigrations
python manage.py migrate

## Firebase Storage (slike proizvoda)

Ovaj projekt može uploadati slike proizvoda na **Firebase Storage** (server-side, preko Django-a).

### Potrebno

1) Firebase projekt s uključenim **Storage**.

2) Service account JSON:
	 - Firebase Console → Project settings → Service accounts → Generate new private key
	 - Spremi JSON lokalno i **ne committaj ga**.

3) Postavi environment varijable:

- `FIREBASE_SERVICE_ACCOUNT_PATH` – putanja do service-account JSON-a
- `FIREBASE_STORAGE_BUCKET` – naziv bucketa
	- npr. `your-project-id.appspot.com` ili `your-project-id.firebasestorage.app`
- `FIREBASE_STORAGE_PUBLIC` (opcionalno) – `1` (default) public URL, `0` signed URL (1h)

### Migracija postojećih slika iz `media/` (opcionalno)

```bash
python manage.py upload_product_images_to_firebase --dry-run
python manage.py upload_product_images_to_firebase
```

Ako želiš prepisati postojeći `image_url`:

```bash
python manage.py upload_product_images_to_firebase --overwrite
```
```
