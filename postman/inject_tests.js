const fs = require('fs');
const collectionPath = './postman/collection.json'; // Adjust as needed

// Simple test script to add to the specific request
const testScript = {
    listen: 'test',
    script: {
        exec: [
            "pm.test('Status code is 200', function () {",
            '    pm.response.to.have.status(200);',
            '});',
        ],
        type: 'text/javascript',
    },
};

// The endpoint you want to add the test to
const targetEndpoint = '/test';

// Read the collection
fs.readFile(collectionPath, 'utf8', (err, data) => {
    if (err) {
        console.error(`Error reading collection file: ${err}`);
        return;
    }

    let collection = JSON.parse(data);

    // Function to extract the URL string from the item's request
    function getUrlString(item) {
        if (item.request && item.request.url) {
            if (typeof item.request.url === 'string') {
                return item.request.url;
            } else if (item.request.url.raw) {
                return item.request.url.raw;
            } else if (item.request.url.path && Array.isArray(item.request.url.path)) {
                // Assuming your URLs are stored as arrays in some items
                return '/' + item.request.url.path.join('/');
            }
            // Add other conditions here if your collection uses different structures
        }
        return '';
    }

    // Function to recursively search and add test script to the targeted item
    const addTestToTarget = (items) => {
        items.forEach(item => {
            // Check if the item is a folder and recurse into its items
            if (item.item) {
                addTestToTarget(item.item);
            } else {
                // Extract the URL string based on the item structure
                const urlString = getUrlString(item);
                // Check if the extracted URL string matches the target endpoint
                if (urlString.endsWith(targetEndpoint)) {
                    if (!item.event) {
                        item.event = [];
                    }
                    item.event.push(testScript);
                    console.log(`Test added to: ${item.name}`);
                }
            }
        });
    };

    // Start the process by passing the collection's items
    addTestToTarget(collection.item);

    // Write the updated collection back to the file
    fs.writeFile(collectionPath, JSON.stringify(collection, null, 2), (err) => {
        if (err) {
            console.error(`Error writing updated collection file: ${err}`);
            return;
        }
        console.log('Collection updated with test scripts for target endpoint.');
    });
});
