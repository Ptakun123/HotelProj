package com.example.aplikacja;

import android.os.Parcel;
import android.os.Parcelable;

import androidx.annotation.NonNull;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;

public class UserAndTokens implements Parcelable {
    String access_token;
    String refresh_token;
    String token_type;
    int user_id;
    String email;
    String first_name;
    String last_name;
    public UserAndTokens() {}
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

    public UserAndTokens(String access_token, String refresh_token, String token_type, int user_id, String email, String first_name, String last_name) {
        this.access_token = access_token;
        this.refresh_token = refresh_token;
        this.token_type = token_type;
        this.user_id = user_id;
        this.email = email;
        this.first_name = first_name;
        this.last_name = last_name;
    }


        public UserAndTokens(JsonNode node){
            this.access_token = node.get("access_token").asText();
            this.refresh_token = node.get("refresh_token").asText();
            this.token_type = node.get("token_type").asText();
            this.user_id = node.get("user").get("id").asInt();
            this.email = node.get("user").get("email").asText();
            this.first_name = node.get("user").get("first_name").asText();
            this.last_name = node.get("user").get("last_name").asText();
        }

    protected UserAndTokens(Parcel in){
        access_token=in.readString();
        refresh_token=in.readString();
        token_type=in.readString();
        user_id=in.readInt();
        email=in.readString();
        first_name=in.readString();
        last_name=in.readString();
    }
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
