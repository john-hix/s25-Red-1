#!/usr/bin/env node
'use strict';



const mock_fs = require("mock-fs");
const oaf = require("openapi-format/openapi-format");

async function main() {
    let data = "";
    for await (const chunk of process.stdin) {
        data += chunk;
    }

    let oaObject = await oaf.parseString(
        data, {
            keepComments: true, 
            bundle: true
        })

    let convertedOpenAPI = await oaf.openapiConvertVersion(
        oaObject, 
        {convertToVersion: 3.1}
    );

    let output = await oaf.stringify(
        convertedOpenAPI.data, 
        {format: "json"}
    );

    console.log(output);
}

main();