-- Keep a log of any SQL queries you execute as you solve the mystery.


-- Desrciption of crime on given day
SELECT description 
FROM crime_scene_reports 
WHERE month = 7 AND day = 28 AND year = 2020
AND street = "Chamberlin Street";
-- Theft of the CS50 duck took place at 10:15am at the Chamberlin Street courthouse. 
-- Interviews were conducted today with three witnesses who were present at the time. 


-- Transcript of interviews from witnesses
SELECT name, transcript 
FROM interviews 
WHERE month = 7 AND day = 28 AND year = 2020 AND transcript LIKE "%courthouse%";
-- Thief entered car within 10 minutes of crime
-- Thief was withdrawing cash at ATM on Fifer Street morning of theft
-- Thief made phone call while leaving courthouse, call lasted less than a minute, thief said they plan to take earliest flight next day, thief asked person on other line to book ticket (accomplice)


-- Get name of thief
SELECT name FROM people 
-- Query courthouse security logs
WHERE people.license_plate IN (
    SELECT license_plate 
    FROM courthouse_security_logs 
    WHERE year = 2020 AND month = 7 AND day = 28 AND hour = 10 AND minute >= 15 AND minute <= 25
)
-- Query ATM transactions
AND people.id IN (
    SELECT person_id
    FROM bank_accounts
    JOIN atm_transactions ON atm_transactions.account_number = bank_accounts.account_number
    WHERE year = 2020 AND month = 7 AND day = 28 AND atm_location = "Fifer Street" AND transaction_type = "withdraw"
)
-- Query phone calls
AND people.phone_number IN (
    SELECT caller 
    FROM phone_calls 
    WHERE year = 2020 AND month = 7 AND day = 28 AND duration < 60
)
-- Query passengers in first flight day after crime
AND people.passport_number IN (
    SELECT passport_number
    FROM passengers
    WHERE flight_id IN (
        SELECT id FROM flights
        WHERE year = 2020 AND month = 7 AND day = 29
        ORDER BY hour, minute LIMIT 1
    )
);


-- Get the city name
SELECT city FROM airports
JOIN flights ON flights.destination_airport_id = airports.id
WHERE year = 2020 AND month = 7 AND day = 29
ORDER BY hour, minute LIMIT 1;


-- Find the accomplice
SELECT name FROM people
WHERE phone_number IN (
    SELECT receiver FROM phone_calls
    WHERE year = 2020 AND month = 7 AND day = 28
    AND caller = (SELECT phone_number FROM people WHERE name = "Ernest")
    AND duration < 60
); 