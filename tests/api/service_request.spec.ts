import { test, expect } from '@playwright/test';

test('Service Request API - create request', async ({ request }) => {

  const response = await request.post(
    'https://admin.citizen-connect.org/api/method/citizen_connect_app.api.service_request.create',
    {
      multipart: {
        service_name: 'j5fr2rb1n8',
        full_name: 'Vivek Gupta',
        email_id: 'vivek@impactyaan.com',
        description: 'i need help for this service'
      }
    }
  );

  console.log('Status:', response.status());

  const responseBody = await response.json();

  console.log('Response:', responseBody);

  expect(response.status()).toBe(200);
});