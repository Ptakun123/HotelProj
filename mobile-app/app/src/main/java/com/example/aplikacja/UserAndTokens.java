package com.example.aplikacja;

// Model przechowujący dane użytkownika oraz tokeny JWT.
// Implementuje Parcelable do przekazywania między aktywnościami.
import android.os.Parcel;
import android.os.Parcelable;

import androidx.annotation.NonNull;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;

public class UserAndTokens implements Parcelable {
    // Token dostępu JWT
    String access_token;
    // Token odświeżający JWT
    String refresh_token;
    // Typ tokena (np. Bearer)
    String token_type;
    // Id użytkownika
    int user_id;
    // Email użytkownika
    String email;
    // Imię i nazwisko użytkownika
    String first_name;
    String last_name;

    // Konstruktor domyślny
    public UserAndTokens() {}

    // Gettery do pól modelu
    public String getAccess_token() {
        return access_token;
    }
    public String getRefresh_token() {
        return refresh_token;
    }
    public String getToken_type() {
        return token_type;
    }
    public int getUser_id() {
        return user_id;
    }
    public String getEmail() {
        return email;
    }
    public String getFirst_name() {
        return first_name;
    }
    public String getLast_name() {
        return last_name;
    }

    // Konstruktor z wszystkimi polami
    public UserAndTokens(String access_token, String refresh_token, String token_type, int user_id, String email, String first_name, String last_name) {
        this.access_token = access_token;
        this.refresh_token = refresh_token;
        this.token_type = token_type;
        this.user_id = user_id;
        this.email = email;
        this.first_name = first_name;
        this.last_name = last_name;
    }

    // Konstruktor z obiektu JSON (np. z odpowiedzi backendu)
    public UserAndTokens(JsonNode node){
        this.access_token = node.get("access_token").asText();
        this.refresh_token = node.get("refresh_token").asText();
        this.token_type = node.get("token_type").asText();
        this.user_id = node.get("user").get("id_user").asInt();
        this.email = node.get("user").get("email").asText();
        this.first_name = node.get("user").get("first_name").asText();
        this.last_name = node.get("user").get("last_name").asText();
    }

    // Konstruktor do odczytu z Parcel (Parcelable)
    protected UserAndTokens(Parcel in){
        access_token=in.readString();
        refresh_token=in.readString();
        token_type=in.readString();
        user_id=in.readInt();
        email=in.readString();
        first_name=in.readString();
        last_name=in.readString();
    }

    // Parcelable CREATOR
    public static final Creator<UserAndTokens> CREATOR = new Creator<UserAndTokens>() {
        @Override
        public UserAndTokens createFromParcel(Parcel in) {
                return new UserAndTokens(in);
        }

        @Override
        public UserAndTokens[] newArray(int size) {
            return new UserAndTokens[size];
        }
    };

    @Override
    public int describeContents() {
        return 0;
    }

    // Zapisuje dane do Parcel (Parcelable)
    @Override
    public void writeToParcel(@NonNull Parcel dest, int flags) {
        dest.writeString(access_token);
        dest.writeString(refresh_token);
        dest.writeString(token_type);
        dest.writeInt(user_id);
        dest.writeString(email);
        dest.writeString(first_name);
        dest.writeString(last_name);
    }
}
