import os

# File paths
FEATURE_FILE_PATH = ("/home/gaurav/Desktop/Order-Orchestration-1/work/integration-tests/src/test/java/features/OOO"
                     "/MultipleFOBopis01.feature")

# Extracting the feature file name without the ".feature" extension
FEATURE_FILE_NAME = os.path.basename(FEATURE_FILE_PATH).replace(".feature", "")

# Extract the base path till "test"
base_path = FEATURE_FILE_PATH.split("/java/")[0]

# Construct the input, expected, featureData, scenarioData  directories paths
INPUT_DIR_PATH = os.path.join(base_path, "resources/input")
EXPECTED_DIR_PATH = os.path.join(base_path, "resources/expected")
FEATUREDATA_DIR_PATH = os.path.join(base_path, "resources/featureData")
SCENARIODATA_DIR_PATH = os.path.join(base_path, "resources/scenarioData")


#Exceptional API's not following Camel Case Convention
DICTIONARY_API = {
    "GETFulfillmentOrderId": "getFOList",
    "GETFODetails": "getFODetails",
}
