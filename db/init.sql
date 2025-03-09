
-- Tabela adresów
CREATE TABLE Addresses (
    id_address SERIAL PRIMARY KEY,
    country CHAR(2) NOT NULL,
    city VARCHAR(50) NOT NULL,
    street VARCHAR(50) NOT NULL,
    building VARCHAR(5) NOT NULL,
    zip_code VARCHAR(15) NOT NULL
);

-- Tabela hoteli
CREATE TABLE Hotels (
    id_hotel SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    geo_length DOUBLE PRECISION NOT NULL,
    geo_latitude DOUBLE PRECISION NOT NULL,
    stars SMALLINT NOT NULL,
    id_address INTEGER NOT NULL REFERENCES Addresses(id_address) ON DELETE CASCADE
);

-- Tabela użytkowników
CREATE TABLE Users (
    id_user SERIAL PRIMARY KEY,
    email VARCHAR(50) UNIQUE NOT NULL,
    password_hash CHAR(64) NOT NULL,
    birth_date DATE NOT NULL,
    first_name VARCHAR(30) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    phone_number CHAR(19) NOT NULL,
    role VARCHAR(10) CHECK (role IN ('A', 'U')) NOT NULL
);

-- Tabela pokojów
CREATE TABLE Rooms (
    id_room SERIAL PRIMARY KEY,
    capacity SMALLINT NOT NULL,
    price_per_night NUMERIC(6,2) NOT NULL,
    id_hotel INTEGER NOT NULL REFERENCES Hotels(id_hotel) ON DELETE CASCADE
);

-- Tabela rezerwacji
CREATE TABLE Reservations (
    id_reservation SERIAL PRIMARY KEY,
    first_night DATE NOT NULL,
    last_night DATE NOT NULL,
    full_name VARCHAR(50) NOT NULL,
    price NUMERIC(10,2) NOT NULL,
    bill_type CHAR(1) CHECK (bill_type IN ('I', 'R')) NOT NULL,
    NIP VARCHAR(20),
    id_room INTEGER NOT NULL REFERENCES Rooms(id_room) ON DELETE CASCADE,
    id_user INTEGER NOT NULL REFERENCES Users(id_user) ON DELETE CASCADE
);

-- Tabela udogodnień hoteli
CREATE TABLE Hotel_facilities (
    id_hotel_facility SERIAL PRIMARY KEY,
    facility_name VARCHAR(50) NOT NULL UNIQUE
);

-- Relacja hotel - udogodnienia
CREATE TABLE Hotels_Hotel_facilities (
    id_hotel INTEGER NOT NULL REFERENCES Hotels(id_hotel) ON DELETE CASCADE,
    id_hotel_facility INTEGER NOT NULL REFERENCES Hotel_facilities(id_hotel_facility) ON DELETE CASCADE,
    PRIMARY KEY (id_hotel, id_hotel_facility)
);

-- Tabela udogodnień pokojów
CREATE TABLE Room_facilities (
    id_room_facility SERIAL PRIMARY KEY,
    facility_name VARCHAR(50) NOT NULL UNIQUE
);

-- Relacja pokój - udogodnienia
CREATE TABLE Rooms_Room_facilities (
    id_room INTEGER NOT NULL REFERENCES Rooms(id_room) ON DELETE CASCADE,
    id_room_facility INTEGER NOT NULL REFERENCES Room_facilities(id_room_facility) ON DELETE CASCADE,
    PRIMARY KEY (id_room, id_room_facility)
);

-- Indeksy
CREATE INDEX IX_Hotel_has_a_room ON Rooms(id_hotel);
CREATE INDEX IX_Room_has_a_reservation ON Reservations(id_room);
CREATE INDEX IX_User_has_a_reservation ON Reservations(id_user);


