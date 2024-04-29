/** @type {import('./$types').PageLoad} */

import { documentData } from '../../../stores/documentData.js';

export async function load({ fetch }) {
    try {
        const response = await fetch('http://localhost:8000/docu/list');
        if (!response.ok) {
            throw new Error('Failed to fetch documents');
        }
        const documentList = await response.json();
        documentData.set(documentList);
        // return {
        //     props: {
        //         documentList
        //     }
        // };
    } catch (error) {
        console.error('Error fetching documents:', error);
        return {
            status: 500,
            error: 'Failed to load documents',
            message: error
        };
    }
}

