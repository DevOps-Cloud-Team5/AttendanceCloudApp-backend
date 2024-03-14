const fs = require('fs');
const collectionPath = './postman/collection.json'; // Adjust as needed

// Simple test script to add to each request
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

// Read the collection
fs.readFile(collectionPath, 'utf8', (err, data) => {
	if (err) {
		console.error(`Error reading collection file: ${err}`);
		return;
	}

	let collection = JSON.parse(data);

	// Inject the test script into each item (request) in the collection
	collection.item.forEach((item) => {
		if (!item.event) {
			item.event = [];
		}
		item.event.push(testScript);
	});

	// Write the updated collection back to the file
	fs.writeFile(collectionPath, JSON.stringify(collection, null, 2), (err) => {
		if (err) {
			console.error(`Error writing updated collection file: ${err}`);
			return;
		}
		console.log('Collection updated with test scripts.');
	});
});
