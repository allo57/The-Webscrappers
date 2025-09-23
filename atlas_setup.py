from pymongo import MongoClient, errors

# --- Connexion ---
URI = "mongodb+srv://williamlauzon_db_user:xIUP91EXb09rMkMQ@the-webscrappers.y0n8a8r.mongodb.net/The-WebScrappers?retryWrites=true&w=majority&appName=The-WebScrappers"
DB_NAME = "The-WebScrappers"
COLL = "produits"

# --- Schéma JSON (validation côté MongoDB) ---
validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["nom", "prix", "url_produit", "url_image", "expedition"],
        "properties": {
            "nom":         {"bsonType": "string", "description": "Nom du produit"},
            "prix":        {"bsonType": ["double", "int", "long", "decimal"], "description": "Prix numerique"},
            "url_produit": {"bsonType": "string", "pattern": r"^https?://", "description": "URL http(s)"},
            "url_image":   {"bsonType": "string", "pattern": r"^https?://", "description": "URL http(s)"},
            "expedition":  {"bsonType": "string", "description": "Type/conditions d'expedition"}
        },
        "additionalProperties": True
    }
}

def ensure_collection_with_schema(db, name, validator):
    # crée la collection si elle n'existe pas, sinon applique/actualise le validator
    if name not in db.list_collection_names():
        db.create_collection(name, validator={"$jsonSchema": validator["$jsonSchema"]})
        print(f"🆕 Collection créée avec schéma: {name}")
    else:
        db.command("collMod", name, validator={"$jsonSchema": validator["$jsonSchema"]})
        print(f"🔧 Schéma mis à jour sur: {name}")

def main():
    try:
        client = MongoClient(URI, serverSelectionTimeoutMS=20000, connectTimeoutMS=20000)
        client.admin.command("ping")
        print("✅ Connexion Atlas OK")
    except errors.PyMongoError as e:
        print(f"❌ Connexion échouée: {e}")
        return

    db = client[DB_NAME]
    print(f"📚 Base sélectionnée: {DB_NAME}")

    # (optionnel) nettoyer anciennes collections si tu ne les veux plus
    for old in ["ordinateurs_jeu", "portables_jeu"]:
        if old in db.list_collection_names():
            db.drop_collection(old)
            print(f"🗑️ Supprimé: {old}")

    # assurer la collection produits avec schéma
    ensure_collection_with_schema(db, COLL, validator)

    col = db[COLL]

    # insérer un exemple (si la collection est vide)
    if col.estimated_document_count() == 0:
        exemple = {
            "nom": "Portable de jeu X15",
            "prix": 1499.99,
            "url_produit": "https://exemple.tld/produit/x15",
            "url_image": "https://exemple.tld/images/x15.jpg",
            "expedition": "Livraison gratuite 2-5 jours"
        }
        col.insert_one(exemple)
        print("📥 Exemple inséré dans 'produits'.")

    # aperçu
    print("📊 Collections:", db.list_collection_names())
    print("➡️ Un doc:", col.find_one({}, {"_id": 0}))

    client.close()
    print("✅ Collection 'produits' prête. Tu pourras importer le CSV ensuite.")

if __name__ == "__main__":
    main()
