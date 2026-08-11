-- -----------------------------------------------------
-- DML Avidex
-- -----------------------------------------------------

-- Ayush Baruah & Joseph Eidel

-- @ symbol used for user filled data

-- -----------------------------------------------------
-- Select Birds
-- -----------------------------------------------------
SELECT birdID, commonName, species, rarityID, callURL, wingspan, size,
    identifyingMarks, range, description, photographURL, matingSeason
FROM Birds
ORDER BY commonName;

-- -----------------------------------------------------
-- Select Birders
-- -----------------------------------------------------
SELECT birderID, birderName, points
FROM Birders
ORDER BY birderName;

-- -----------------------------------------------------
-- Select Sightings with inner joins on bird and birder
-- -----------------------------------------------------
SELECT Sightings.sightingID,
    Sightings.birderID,
    Birders.birderID,
    Sightings.birdID,
    Birders.birderName,
    Birds.commonName,
    Sightings.birdCount,
    Sightings.gpsLocation,
    Sightings.time
FROM Sightings
    INNER JOIN Birders ON Sightings.birderID = Birders.birderID
    INNER JOIN Birds ON Sightings.birdID = Birds.birdID
    ORDER BY Sightings.time;

-- -----------------------------------------------------
-- Select Bird Lists joining BirdsList and Birders on bird.ID
-- -----------------------------------------------------
SELECT BirdsList.birderID,
       Birders.birderName,
       BirdsList.birdID,
       Birds.commonName,
       BirdsList.count,
       Birds.rarityID
FROM BirdsList
    INNER JOIN Birds   ON BirdsList.birdID   = Birds.birdID
    ORDER BY Birds.commonName;

-- -----------------------------------------------------
-- Select Rarities
-- -----------------------------------------------------
SELECT rarityID
FROM Rarities
ORDER BY rarityID;

-- -----------------------------------------------------
-- Select Nests
-- -----------------------------------------------------
SELECT nestID, type, location
FROM Nests
ORDER BY type, location;

-- -----------------------------------------------------
-- Select Rewards
-- -----------------------------------------------------
SELECT rewardID, name, description, threshold
FROM Rewards
ORDER BY threshold;


-- -----------------------------------------------------
-- Select Bird Nests with inner joins of birdID and nestID
-- -----------------------------------------------------
SELECT BirdsNests.birdID,
       Birds.commonName,
       BirdsNests.nestID,
       Nests.type,
       Nests.location
FROM BirdsNests
    INNER JOIN Birds ON BirdsNests.birdID = Birds.birdID
    INNER JOIN Nests ON BirdsNests.nestID = Nests.nestID
    ORDER BY Birds.commonName;

-- -----------------------------------------------------
-- Select Birder Rewards with inner joins on birderID and rewardID
-- -----------------------------------------------------
SELECT BirdersRewards.birderID,
       Birders.birderName,
       BirdersRewards.rewardID,
       Rewards.name,
       Rewards.threshold
FROM BirdersRewards
    INNER JOIN Birders ON BirdersRewards.birderID = Birders.birderID
    INNER JOIN Rewards ON BirdersRewards.rewardID = Rewards.rewardID
    ORDER BY Birders.birderName, Rewards.threshold;

-- -----------------------------------------------------
-- Bird Dropdown
-- -----------------------------------------------------
SELECT birdID, commonName
FROM Birds
ORDER BY commonName;

-- -----------------------------------------------------
-- Birder Dropdown
-- -----------------------------------------------------
SELECT birderID, birderName
FROM Birders
ORDER BY birderName;

-- -----------------------------------------------------
-- Insert a bird species
-- -----------------------------------------------------
INSERT INTO Birds
    (commonName, species, rarityID, callUrl, wingspan, size, identifyingMarks, 
    range, description, photographUrl, matingSeason)
VALUES
    (@commonName, @species, @rarityID, @callUrl, @wingspan, @size, @identifyingMarks, @range, 
    @description, @photographUrl, @matingSeason);

-- -----------------------------------------------------
-- Update a Bird
-- -----------------------------------------------------
UPDATE Birds
SET commonName = @commonName,
    species = @species,
    rarityID= @rarityID,
    callUrl = @callUrl,
    wingspan = @wingspan,
    size = :size,
    identifyingMarks = @identifyingMarks,
    range = @range,
    description = @description,
    photographUrl = @photographUrl,
    matingSeason = @matingSeason
WHERE birdID = @birdID;

-- -----------------------------------------------------
-- Add a sighting
-- -----------------------------------------------------
INSERT INTO Sightings (birderID, birdID, birdCount, gpsLocation, time)
VALUES (@birderID, @birdID, @birdCount, @gpsLocation, @time);

-- -----------------------------------------------------
-- Delete a bird CASCADEs to that bird's sightings, bird list rows, and BirdsNests intersection table
-- -----------------------------------------------------
DELETE FROM Birds WHERE birdID = @birdID;

-- -----------------------------------------------------
-- Delete a sighting
-- -----------------------------------------------------
DELETE FROM Sightings WHERE sightingID = @sightingID;

-- -----------------------------------------------------
-- Delete a birder CASCADEs to that birder's sighting, bird list, and rewards
-- -----------------------------------------------------
DELETE FROM Birders WHERE birderID = @birderID;


-- Added 08/09/26 for CUD for BirderRewards table (M:N relationship between Birders and Rewards)
-- -----------------------------------------------------
-- Reward Dropdown. Populates the reward select element 
-- on the BirdersRewards page
-- -----------------------------------------------------
SELECT rewardID, name
FROM Rewards
ORDER BY name;


-- -----------------------------------------------------
-- Add a BirderReward
-- -----------------------------------------------------
INSERT INTO BirdersRewards (birderID, rewardID)
VALUES (@birderID, @rewardID);

-- -----------------------------------------------------
--Update a BirderReward
-- -----------------------------------------------------
UPDATE BirdersRewards
SET birderID = @newBirderID,
    rewardID = @newRewardID
WHERE birderID = @oldBirderID
  AND rewardID = @oldRewardID;

-- -----------------------------------------------------
-- Delete a BirderReward
-- -----------------------------------------------------
DELETE FROM BirdersRewards
WHERE birderID = @birderID
  AND rewardID = @rewardID;
