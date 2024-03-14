// convert_schema.js

const fs = require('fs');
const openapiToPostman = require('openapi-to-postmanv2');

// Retrieve command-line arguments for file paths
const [, , openApiSpecPath, postmanCollectionPath] = process.argv;

// Check if the OpenAPI spec path and Postman collection path are provided
if (!openApiSpecPath || !postmanCollectionPath) {
	console.error(
		'Usage: node convert_schema.js <OpenAPI Spec Path> <Postman Collection Path>',
	);
	process.exit(1);
}

// Read the OpenAPI spec file
fs.readFile(openApiSpecPath, 'utf8', (err, data) => {
	if (err) {
		console.error(`Error reading OpenAPI spec file: ${err.message}`);
		process.exit(1);
	}

	// Convert the OpenAPI spec to a Postman collection
	openapiToPostman.convert(
		{ type: 'string', data: data },
		{},
		(err, conversionResult) => {
			if (err) {
				console.error(`Conversion error: ${err.message}`);
				process.exit(1);
			}

			if (!conversionResult.result) {
				console.error(`Conversion failed: ${conversionResult.reason}`);
				process.exit(1);
			}

			// Write the Postman collection to the specified output path
			fs.writeFile(
				postmanCollectionPath,
				JSON.stringify(conversionResult.output[0].data, null, 2),
				(err) => {
					if (err) {
						console.error(
							`Error writing Postman collection file: ${err.message}`,
						);
						process.exit(1);
					}

					console.log(
						`Postman collection generated successfully at ${postmanCollectionPath}`,
					);
				},
			);
		},
	);
});
