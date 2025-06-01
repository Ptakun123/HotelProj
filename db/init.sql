
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

-- Tabeli zdjęć hoteli
CREATE TABLE Hotel_images (
    id_image SERIAL PRIMARY KEY,
    id_hotel INTEGER NOT NULL REFERENCES Hotels(id_hotel) ON DELETE CASCADE,
    image_url VARCHAR(255) NOT NULL,
    description VARCHAR(100),
    is_main BOOLEAN DEFAULT FALSE
);

-- Tabela użytkowników
CREATE TABLE Users (
    id_user SERIAL PRIMARY KEY,
    email VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
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
    nip VARCHAR(20),
    reservation_status CHAR(1) CHECK (reservation_status IN ('A', 'C')) NOT NULL,
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
CREATE INDEX IX_Hotel_images ON Hotel_images(id_hotel);

-- DODANIE WARTOŚCI POCZĄTKOWYCH --

-- Dodanie adresów
INSERT INTO Addresses (country, city, street, building, zip_code) VALUES
('PL', 'Warsaw', 'Main Street', '10A', '00-001'),
('PL', 'Krakow', 'Market Square', '5', '30-001'),
('PL', 'Gdansk', 'Długa', '20', '80-834'),
('DE', 'Berlin', 'Unter den Linden', '17', '10117'),
('FR', 'Paris', 'Champs-Élysées', '100', '75008'),
('ES', 'Madrid', 'Gran Vía', '30', '28013'),
('IT', 'Rome', 'Via del Corso', '150', '00186'),
('UK', 'London', 'Oxford Street', '250', 'W1C 1AB'),
('PL', 'Wrocław', 'Rynek', '25', '50-101'),
('PL', 'Poznań', 'Stary Rynek', '77', '61-772'),
('PL', 'Zakopane', 'Krupówki', '40', '34-500'),
('SK', 'Bratislava', 'Hviezdoslavovo námestie', '18', '811 02');


-- Dodanie hoteli
INSERT INTO Hotels (name, geo_length, geo_latitude, stars, id_address) VALUES
('Hotel Warsaw Centre', 21.0122, 52.2297, 5, 1),
('Hotel Krakow Old Town', 19.9445, 50.0647, 4, 2),
('Hilton Gdansk', 18.6534, 54.3499, 5, 3),
('Hotel Adlon Kempinski', 13.3777, 52.5162, 5, 4),
('Hotel Ritz Paris', 2.3297, 48.8672, 5, 5),
('Hotel Rosalia Madrid', -3.7038, 40.4168, 3, 6),
('Hotel Artemide Rome', 12.4890, 41.9028, 4, 7),
('The Langham London', -0.1469, 51.5186, 5, 8),
('Radisson Blu Hotel, Wrocław', 17.0326, 51.1107, 5, 9),
('Hotel Puro Poznań Stare Miasto', 16.9287, 52.4087, 4, 10),
('Hotel Mercure Kasprowy Zakopane', 19.9575, 49.2941, 3, 11),
('Radisson Blu Carlton Hotel, Bratislava', 17.1106, 48.1408, 4, 12);


-- Dodanie zdjęć hoteli (po jednym głównym zdjęciu dla każdego hotelu)
INSERT INTO Hotel_images (id_hotel, image_url, description, is_main) VALUES
(1, 'http://localhost:8888/images/hotels/warsaw_main.jpg', 'Główne wejście', TRUE),
(2, 'http://localhost:8888/images/hotels/krakow_market.jpg', 'Hotel na Rynku', TRUE),
(3, 'http://localhost:8888/images/hotels/gdansk_hilton_exterior.jpg', 'Hilton Gdansk z zewnątrz', TRUE),
(4, 'http://localhost:8888/images/hotels/berlin_adlon_lobby.jpg', 'Lobby Adlon Kempinski', TRUE),
(5, 'http://localhost:8888/images/hotels/paris_ritz_garden.jpg', 'Ogrody Ritz', TRUE),
(6, 'http://localhost:8888/images/hotels/madrid_rosalia_exterior.jpg', 'Hotel Rosalia Madryt', TRUE),
(7, 'http://localhost:8888/images/hotels/rome_artemide_facade.jpg', 'Fasada Artemide', TRUE),
(8, 'http://localhost:8888/images/hotels/london_langham_front.jpg', 'Wejście do Langham', TRUE),
(9, 'http://localhost:8888/images/hotels/wroclaw_radisson_exterior.jpg', 'Radisson Blu Wrocław', TRUE),
(10, 'http://localhost:8888/images/hotels/poznan_puro_exterior.jpg', 'Puro Poznań', TRUE),
(11, 'http://localhost:8888/images/hotels/zakopane_mercure_mountains.jpg', 'Widok na góry', TRUE),
(12, 'http://localhost:8888/images/hotels/bratislava_carlton_exterior.jpg', 'Carlton Bratysława', TRUE),
(13, 'http://localhost:8888/images/hotels/warsaw_lobby.jpg', 'Główne wejście', FALSE),
(14, 'http://localhost:8888/images/hotels/warsaw_room.jpg', 'Główne wejście', FALSE);


-- Dodanie użytkowników
INSERT INTO Users (email, password_hash, birth_date, first_name, last_name, phone_number, role) VALUES
('admin@example.com', 'd033e22ae348aeb5660fc2140aec35850c4da997', '1980-01-01', 'Admin', 'User', '+48123456789', 'A'),
('user1@example.com', '5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8', '1990-05-15', 'John', 'Doe', '+48123456788', 'U');

-- Dodanie pokojów
INSERT INTO Rooms (capacity, price_per_night, id_hotel) VALUES
(2, 200.00, 1), (4, 400.00, 1),
(2, 180.00, 2), (3, 350.00, 2),
(2, 300.00, 3), (3, 450.00, 3),
(2, 500.00, 4), (1, 400.00, 4),
(2, 600.00, 5), (4, 900.00, 5),
(2, 150.00, 6), (3, 250.00, 6),
(2, 220.00, 7), (3, 380.00, 7),
(2, 700.00, 8), (4, 1000.00, 8),
(2, 320.00, 9), (3, 450.00, 9),
(2, 380.00, 10), (4, 550.00, 10),
(2, 200.00, 11), (3, 290.00, 11),
(2, 250.00, 12), (3, 350.00, 12);


-- Dodanie udogodnień hoteli
INSERT INTO Hotel_facilities (facility_name) VALUES
('WiFi'), ('Parking'), ('Swimming Pool'), ('Gym'), ('Restaurant'), ('Spa'), ('Conference Room'), ('Pet-Friendly');


-- Dodanie udogodnień pokojów
INSERT INTO Room_facilities (facility_name) VALUES
('Air Conditioning'), ('TV'), ('Mini Bar'), ('Balcony'), ('Bathtub'), ('Coffee Machine');


-- Dodanie rezerwacji
INSERT INTO Reservations (first_night, last_night, full_name, price, bill_type, nip, reservation_status, id_room, id_user) VALUES
('2025-06-10', '2025-06-15', 'John Doe', 1000.00, 'I', NULL, 'A', 1, 2);

-- Relacja hotel - udogodnienia
INSERT INTO Hotels_Hotel_facilities (id_hotel, id_hotel_facility) VALUES
(1, 1), (1, 2), (1, 3), (1, 4), (1, 5),
(2, 1), (2, 5),
(3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (3, 6),
(4, 1), (4, 5), (4, 6), (4, 7),
(5, 1), (5, 5), (5, 6), (5, 8),
(6, 1), (6, 2), (6, 5),
(7, 1), (7, 5),
(8, 1), (8, 3), (8, 4), (8, 5), (8, 6), (8, 7),
(9, 1), (9, 2), (9, 4), (9, 5), (9, 6), (9, 7),
(10, 1), (10, 2), (10, 5), (10, 8),
(11, 1), (11, 2), (11, 3), (11, 4), (11, 5),
(12, 1), (12, 5), (12, 7);


-- Relacja pokój - udogodnienia
INSERT INTO Rooms_Room_facilities (id_room, id_room_facility) VALUES
(1, 1), (1, 2), (1, 3),
(2, 1), (2, 2), (2, 4),
(3, 1), (3, 2),
(4, 1), (4, 2), (4, 3),
(5, 1), (5, 2), (5, 4),
(6, 1), (6, 2),
(7, 1), (7, 2), (7, 3),
(8, 1), (8, 2), (8, 4),
(9, 1), (9, 2), (9, 3),
(10, 1), (10, 2), (10, 5),
(11, 1), (11, 2), (11, 6),
(12, 1), (12, 2), (12, 3), (12, 4), (12, 5),
(13, 1), (13, 2), (13, 3),
(14, 1), (14, 2), (14, 4),
(15, 1), (15, 2),
(16, 1), (16, 2), (16, 3),
(17, 1), (17, 2), (17, 4),
(18, 1), (18, 2),
(19, 1), (19, 2), (19, 3),
(20, 1), (20, 2), (20, 4),
(21, 1), (21, 2),
(22, 1), (22, 2), (22, 3),
(23, 1), (23, 2), (23, 4),
(24, 1), (24, 2);
