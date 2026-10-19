import { test, expect } from '@playwright/test';


const BASE_URL =
  process.env.API_BASE_URL || 'https://admin.citizen-connect.org';

const USER_SID = process.env.USER_SID;

// Valid Service document for Service GET API
const SERVICE_ID =
  process.env.SERVICE_ID || 'j62t62lsq6';

// Service value accepted by service_request.create
const SERVICE_REQUEST_SERVICE =
  process.env.SERVICE_REQUEST_SERVICE || '926ssg5f3d';

// Issue category
const ISSUE_CATEGORY =
  process.env.ISSUE_CATEGORY || 'Water governance & risk';


// =====================================================
// SERVICE REQUEST - GUEST
// =====================================================

test('Service Request API - Guest user', async ({ request }) => {
  const response = await request.post(
    `${BASE_URL}/api/method/citizen_connect_app.api.service_request.create`,
    {
      multipart: {
        age: '21',
        description: 'I need help with this service',
        service_name: SERVICE_REQUEST_SERVICE,
        full_name: 'Playwright Guest User',
        email_id: 'playwright.guest@example.com',
      },
    }
  );

  const responseBody = await response.json();

  console.log(
    'Guest Service Request Status:',
    response.status()
  );

  console.log(
    'Guest Service Request Response:',
    responseBody
  );

  expect(response.status()).toBe(200);
  expect(responseBody.status).toBe('success');
  expect(responseBody.message).toBe(
    'Request submitted successfully'
  );

  expect(responseBody.data).toBeTruthy();
  expect(responseBody.data.name).toBeTruthy();
  expect(responseBody.data.status).toBe('New');
});


// =====================================================
// SERVICE REQUEST - LOGGED-IN USER
// =====================================================

test('Service Request API - Logged-in user', async ({ request }) => {
  expect(USER_SID).toBeTruthy();

  const response = await request.post(
    `${BASE_URL}/api/method/citizen_connect_app.api.service_request.create`,
    {
      multipart: {
        age: '21',
        description: 'I need help with this service',
        service_name: SERVICE_REQUEST_SERVICE,
      },

      headers: {
        Cookie: `sid=${USER_SID}`,
      },
    }
  );

  const responseBody = await response.json();

  console.log(
    'Logged-in Service Request Status:',
    response.status()
  );

  console.log(
    'Logged-in Service Request Response:',
    responseBody
  );

  expect(response.status()).toBe(200);
  expect(responseBody.status).toBe('success');
  expect(responseBody.message).toBe(
    'Request submitted successfully'
  );

  expect(responseBody.data).toBeTruthy();
  expect(responseBody.data.name).toBeTruthy();
  expect(responseBody.data.status).toBe('New');
});


// =====================================================
// ISSUE - GUEST
// =====================================================

test('Issue API - Guest user', async ({ request }) => {
  const requestData = {
    title: 'Guest test issue',

    description: 'Issue created by guest user',

    category: JSON.stringify({
      l1: ISSUE_CATEGORY,
    }),

    urgency: 'High',

    location: JSON.stringify({
      country: 'India',
      geo1: 'Maharashtra',
      geo2: 'Pune',
    }),

    allow_contact: 'true',
  };

  const response = await request.post(
    `${BASE_URL}/api/method/citizen_connect_app.api.issue.create_issue`,
    {
      multipart: requestData,
    }
  );

  const responseBody = await response.json();

  console.log(
    'Guest Issue Status:',
    response.status()
  );

  console.log(
    'Guest Issue Response:',
    responseBody
  );

  expect(response.status()).toBe(200);
  expect(responseBody.status).toBe('success');
});


// =====================================================
// ISSUE - LOGGED-IN USER
// =====================================================

test('Issue API - Logged-in user', async ({ request }) => {
  expect(USER_SID).toBeTruthy();

  const requestData = {
    title: 'Logged-in user test issue',

    description: 'Issue created by logged-in user',

    category: JSON.stringify({
      l1: ISSUE_CATEGORY,
    }),

    urgency: 'High',

    location: JSON.stringify({
      country: 'India',
      geo1: 'Maharashtra',
      geo2: 'Pune',
    }),

    allow_contact: 'true',
  };

  const response = await request.post(
    `${BASE_URL}/api/method/citizen_connect_app.api.issue.create_issue`,
    {
      multipart: requestData,

      headers: {
        Cookie: `sid=${USER_SID}`,
      },
    }
  );

  const responseBody = await response.json();

  console.log(
    'Logged-in Issue Status:',
    response.status()
  );

  console.log(
    'Logged-in Issue Response:',
    responseBody
  );

  expect(response.status()).toBe(200);
  expect(responseBody.status).toBe('success');
});


// =====================================================
// COMMUNITY CHECK - GUEST
// =====================================================

test('Community Check API - Guest user', async ({ request }) => {
  const requestData = {
    description:
      'Water supply and electricity are working properly. Roads are in good condition.',

    electricity: 'Available',

    location: JSON.stringify({
      country: 'India',
      geo1: 'Maharashtra',
      geo2: 'Pune',
    }),

    road: 'Good Condition',
    teacher_at_school: 'Present',
    healthcare: 'Regular',
    internet: 'Good',
    sanitation: 'Functional',
    local_governance: 'Functional',
    confidence_level: 'Very Confident',
    water_supply: 'Available',
  };

  const response = await request.post(
    `${BASE_URL}/api/method/citizen_connect_app.api.community_check.create_community_check`,
    {
      multipart: requestData,
    }
  );

  const responseBody = await response.json();

  console.log(
    'Guest Community Check Status:',
    response.status()
  );

  console.log(
    'Guest Community Check Response:',
    responseBody
  );

  expect(response.status()).toBe(200);
  expect(responseBody.status).toBe('success');
});


// =====================================================
// COMMUNITY CHECK - LOGGED-IN USER
// =====================================================

test('Community Check API - Logged-in user', async ({ request }) => {
  expect(USER_SID).toBeTruthy();

  const requestData = {
    description:
      'Logged-in user community check - water and electricity are working properly.',

    electricity: 'Available',

    location: JSON.stringify({
      country: 'India',
      geo1: 'Maharashtra',
      geo2: 'Pune',
    }),

    road: 'Good Condition',
    teacher_at_school: 'Present',
    healthcare: 'Regular',
    internet: 'Good',
    sanitation: 'Functional',
    local_governance: 'Functional',
    confidence_level: 'Very Confident',
    water_supply: 'Available',
  };

  const response = await request.post(
    `${BASE_URL}/api/method/citizen_connect_app.api.community_check.create_community_check`,
    {
      multipart: requestData,

      headers: {
        Cookie: `sid=${USER_SID}`,
      },
    }
  );

  const responseBody = await response.json();

  console.log(
    'Logged-in Community Check Status:',
    response.status()
  );

  console.log(
    'Logged-in Community Check Response:',
    responseBody
  );

  expect(response.status()).toBe(200);
  expect(responseBody.status).toBe('success');
});



test('Post API - Guest user should be rejected', async ({ request }) => {
  const response = await request.post(
    `${BASE_URL}/api/method/citizen_connect_app.api.post.create`,
    {
      multipart: {
        description: 'Guest should not be able to create post',

        category: JSON.stringify({
          l1: 'Water governance & risk',
        }),

        location: JSON.stringify({
          country: 'India',
          geo1: 'Maharashtra',
          geo2: 'Pune',
        }),
      },
    }
  );

  const responseBody = await response.json();

  console.log('Guest Post Status:', response.status());
  console.log('Guest Post Response:', responseBody);

  expect(response.status()).not.toBe(200);
});


// =====================================================
// POST - LOGGED-IN USER
// =====================================================

test('Post API - Logged-in user and verify Post', async ({
  request,
}) => {
  expect(USER_SID).toBeTruthy();

  const description =
    'This is a Playwright test post from logged-in user';

  const response = await request.post(
    `${BASE_URL}/api/method/citizen_connect_app.api.post.create`,
    {
      multipart: {
        description,

        category: JSON.stringify({
          l1: 'Water governance & risk',
        }),

        location: JSON.stringify({
          country: 'India',
          geo1: 'Maharashtra',
          geo2: 'Pune',
        }),
      },

      headers: {
        Cookie: `sid=${USER_SID}`,
      },
    }
  );

  const responseBody = await response.json();

  console.log('Post Status:', response.status());
  console.log('Post Response:', responseBody);

  expect(response.status()).toBe(200);
  expect(responseBody.status).toBe('success');

  expect(responseBody.data).toBeTruthy();
  expect(responseBody.data.name).toBeTruthy();

  const postData = responseBody.data;

  expect(postData.description).toBe(description);
  expect(postData.category_l1).toBe('Water governance & risk');
  expect(postData.country).toBe('India');
  expect(postData.geography_l1).toBeTruthy();
  expect(postData.geography_l2).toBeTruthy();

  expect(postData.media).toEqual([]);
});
// =====================================================
// VOLUNTEER ACTION - GUEST
// Guest cannot create Volunteer Action
// =====================================================

test(
  'Volunteer Action API - Guest user should be rejected',
  async ({ request }) => {
    const requestData = {
      category: JSON.stringify({
        l1: 'Livelihoods',
        l2: 'Worker environment & rights',
      }),

      description:
        'Guest should not be able to create Volunteer Action',

      location: JSON.stringify({
        country: 'India',
        geo1: 'Maharashtra',
        geo2: 'Pune',
      }),
    };

    const response = await request.post(
      `${BASE_URL}/api/method/citizen_connect_app.api.volunteer_action.create`,
      {
        multipart: requestData,
      }
    );

    const responseBody = await response.json();

    console.log(
      'Guest Volunteer Action Status:',
      response.status()
    );

    console.log(
      'Guest Volunteer Action Response:',
      responseBody
    );

    expect(response.status()).not.toBe(200);
  }
);


// =====================================================
// VOLUNTEER ACTION - LOGGED-IN USER
// =====================================================

test(
  'Volunteer Action API - Logged-in user',
  async ({ request }) => {
    expect(USER_SID).toBeTruthy();

    const requestData = {
      category: JSON.stringify({
        l1: 'Livelihoods',
        l2: 'Worker environment & rights',
      }),

      description:
        'This is a new Volunteer Action from Playwright',

      location: JSON.stringify({
        country: 'India',
        geo1: 'Maharashtra',
        geo2: 'Pune',
      }),

      files: '',
      start_date: '',
      end_date: '',
    };

    const response = await request.post(
      `${BASE_URL}/api/method/citizen_connect_app.api.volunteer_action.create`,
      {
        multipart: {
          category: requestData.category,
          description: requestData.description,
          location: requestData.location,
          files: requestData.files,
          start_date: requestData.start_date,
          end_date: requestData.end_date,
        },

        headers: {
          Cookie: `sid=${USER_SID}`,
        },
      }
    );

    const responseBody = await response.json();

    console.log(
      'Volunteer Action Status:',
      response.status()
    );

    console.log(
      'Volunteer Action Response:',
      responseBody
    );

    expect(response.status()).toBe(200);
    expect(responseBody.status).toBe('success');

    expect(responseBody.data).toBeTruthy();

    expect(responseBody.data.name).toBeTruthy();
    expect(responseBody.data.user).toBeTruthy();

    expect(responseBody.data.category_l1).toBe(
      'Livelihoods'
    );

    expect(responseBody.data.description).toBe(
      requestData.description
    );

    expect(responseBody.data.country).toBe('India');

    expect(responseBody.data.geo_l1).toBeTruthy();
    expect(responseBody.data.geo_l2).toBeTruthy();
  }
);


// =====================================================
// SERVICE GET - GUEST
// =====================================================


test(
  'Service API - Logged-in user can view service',
  async ({ request }) => {
    expect(USER_SID).toBeTruthy();

    const response = await request.get(
      `${BASE_URL}/api/method/citizen_connect_app.api.service.get?service_id=${SERVICE_ID}`,
      {
        headers: {
          Cookie: `sid=${USER_SID}`,
        },
      }
    );

    const responseBody = await response.json();

    console.log('Logged-in Service GET Status:', response.status());
    console.log('Logged-in Service GET Response:', responseBody);

    // 1. Validate HTTP status
    expect(response.status()).toBe(200);

    // 2. Validate top-level response keys
    expect(responseBody).toHaveProperty('status');
    expect(responseBody).toHaveProperty('message');
    expect(responseBody).toHaveProperty('data');

    // 3. Validate service data exists
    expect(responseBody.data).toBeTruthy();

    const data = responseBody.data;

    // 4. Validate service keys
    expect(data).toHaveProperty('id');
    expect(data).toHaveProperty('title');
    expect(data).toHaveProperty('description');
    expect(data).toHaveProperty('location');
    expect(data).toHaveProperty('cost_model');
    expect(data).toHaveProperty('cost_details');
    expect(data).toHaveProperty('availability_status');
    expect(data).toHaveProperty('is_financial_support');
    expect(data).toHaveProperty('service_channel');
    expect(data).toHaveProperty('service_status');
    expect(data).toHaveProperty('creation');
    expect(data).toHaveProperty('modified');
    expect(data).toHaveProperty('eligibility_condition');
    expect(data).toHaveProperty('rating');
    expect(data).toHaveProperty('ngo_name');
    expect(data).toHaveProperty('mobile_number');
    expect(data).toHaveProperty('email_id');
    expect(data).toHaveProperty('whatsapp_mobile_number');
    expect(data).toHaveProperty('service_category');

    // 5. Validate location keys
    expect(data.location).toHaveProperty('country');
    expect(data.location).toHaveProperty('geo1');
    expect(data.location).toHaveProperty('geo2');

    // 6. Validate country keys
    expect(data.location.country).toHaveProperty('name');
    expect(data.location.country).toHaveProperty('display_name');

    // 7. Validate service category keys
    expect(data.service_category).toHaveProperty('l1');
    expect(data.service_category).toHaveProperty('l2');

    expect(data.service_category.l1).toHaveProperty('name');
    expect(data.service_category.l1).toHaveProperty('display_name');

    expect(data.service_category.l2).toHaveProperty('name');
    expect(data.service_category.l2).toHaveProperty('display_name');
  }
);

// =====================================================
// SCHEME GET - GUEST
// =====================================================
test(
  'Scheme API - Guest user can view scheme',
  async ({ request }) => {
    const schemeId = '675nsbimi5';

    const response = await request.get(
      `${BASE_URL}/api/method/citizen_connect_app.api.scheme.get?scheme_id=${schemeId}`
    );

    const responseBody = await response.json();

    console.log('Guest Scheme GET Status:', response.status());
    console.log('Guest Scheme GET Response:', responseBody);

    // 1. Validate HTTP status
    expect(response.status()).toBe(200);

    // 2. Validate top-level response keys
    expect(responseBody).toHaveProperty('message');
    expect(responseBody).toHaveProperty('status');
    expect(responseBody).toHaveProperty('data');

    // 3. Validate scheme data exists
    expect(responseBody.data).toBeTruthy();

    const data = responseBody.data;

    // 4. Validate scheme keys
    expect(data).toHaveProperty('id');
    expect(data).toHaveProperty('scheme_name');
    expect(data).toHaveProperty('description');
    expect(data).toHaveProperty('benefits');
    expect(data).toHaveProperty('eligibility');
    expect(data).toHaveProperty('documents_required');
    expect(data).toHaveProperty('application_url');
    expect(data).toHaveProperty('location');
    expect(data).toHaveProperty('gender');
    expect(data).toHaveProperty('disabled_relevant');
    expect(data).toHaveProperty('income_limit');
    expect(data).toHaveProperty('currency');
    expect(data).toHaveProperty('issuing_body');
    expect(data).toHaveProperty('is_active');
    expect(data).toHaveProperty('is_verified');
    expect(data).toHaveProperty('rating');
    expect(data).toHaveProperty('creation');
    expect(data).toHaveProperty('modified');
    expect(data).toHaveProperty('scheme_category');
    expect(data).toHaveProperty('ngos');

    // 5. Validate location keys
    expect(data.location).toHaveProperty('country');
    expect(data.location).toHaveProperty('geo1');
    expect(data.location).toHaveProperty('geo2');

    // 6. Validate country keys
    expect(data.location.country).toHaveProperty('name');
    expect(data.location.country).toHaveProperty('display_name');

    // 7. Validate scheme category keys
    expect(data.scheme_category).toHaveProperty('l1');
    expect(data.scheme_category).toHaveProperty('l2');

    expect(data.scheme_category.l1).toHaveProperty('name');
    expect(data.scheme_category.l1).toHaveProperty('display_name');

    expect(data.scheme_category.l2).toHaveProperty('name');
    expect(data.scheme_category.l2).toHaveProperty('display_name');

    // 8. Validate NGO entries are available as a field
    expect(Array.isArray(data.ngos)).toBe(true);
  }
);

// =====================================================
// SCHEME GET - LOGGED-IN
// =====================================================

test(
  'Scheme API - Logged-in user can view scheme',
  async ({ request }) => {
    expect(USER_SID).toBeTruthy();

    const schemeId = 'cb2qq247pj';

    const response = await request.get(
      `${BASE_URL}/api/method/citizen_connect_app.api.scheme.get?scheme_id=${schemeId}`,
      {
        headers: {
          Cookie: `sid=${USER_SID}`,
        },
      }
    );

    const responseBody = await response.json();

    console.log(
      'Logged-in Scheme GET Status:',
      response.status()
    );

    console.log(
      'Logged-in Scheme GET Response:',
      responseBody
    );

    // 1. Validate HTTP status
    expect(response.status()).toBe(200);

    // 2. Validate top-level response keys
    expect(responseBody).toHaveProperty('message');
    expect(responseBody).toHaveProperty('status');
    expect(responseBody).toHaveProperty('data');

    // 3. Validate scheme data exists
    expect(responseBody.data).toBeTruthy();

    const data = responseBody.data;

    // 4. Validate scheme keys
    expect(data).toHaveProperty('id');
    expect(data).toHaveProperty('scheme_name');
    expect(data).toHaveProperty('description');
    expect(data).toHaveProperty('benefits');
    expect(data).toHaveProperty('eligibility');
    expect(data).toHaveProperty('documents_required');
    expect(data).toHaveProperty('application_url');
    expect(data).toHaveProperty('location');
    expect(data).toHaveProperty('gender');
    expect(data).toHaveProperty('disabled_relevant');
    expect(data).toHaveProperty('income_limit');
    expect(data).toHaveProperty('currency');
    expect(data).toHaveProperty('issuing_body');
    expect(data).toHaveProperty('is_active');
    expect(data).toHaveProperty('is_verified');
    expect(data).toHaveProperty('rating');
    expect(data).toHaveProperty('creation');
    expect(data).toHaveProperty('modified');
    expect(data).toHaveProperty('scheme_category');
    expect(data).toHaveProperty('ngos');

    // 5. Validate location keys
    expect(data.location).toHaveProperty('country');
    expect(data.location).toHaveProperty('geo1');
    expect(data.location).toHaveProperty('geo2');

    // 6. Validate country keys
    expect(data.location.country).toHaveProperty('name');
    expect(data.location.country).toHaveProperty('display_name');

    // 7. Validate scheme category keys
    expect(data.scheme_category).toHaveProperty('l1');
    expect(data.scheme_category).toHaveProperty('l2');

    expect(data.scheme_category.l1).toHaveProperty('name');
    expect(data.scheme_category.l1).toHaveProperty('display_name');

    expect(data.scheme_category.l2).toHaveProperty('name');
    expect(data.scheme_category.l2).toHaveProperty('display_name');

    // 8. Validate NGOs field is an array
    expect(Array.isArray(data.ngos)).toBe(true);
  }
);

// =====================================================
// VOLUNTEER OPPORTUNITY GET LIST - GUEST
// =====================================================

test(
  'Volunteer Opportunity List API - Guest user can view opportunities',
  async ({ request }) => {
    const response = await request.get(
      `${BASE_URL}/api/method/citizen_connect_app.api.volunteer_opportunity.get_list`
    );

    const responseBody = await response.json();

    console.log(
      'Guest Volunteer Opportunity List Status:',
      response.status()
    );

    console.log(
      'Guest Volunteer Opportunity List Response:',
      responseBody
    );

    expect(response.status()).toBe(200);
    expect(responseBody.status).toBe('success');

    expect(responseBody.data).toBeTruthy();

    expect(
      Array.isArray(responseBody.data.opportunities)
    ).toBe(true);

    expect(responseBody.data.limit).toBe(10);
    expect(responseBody.data.offset).toBe(0);

    expect(
      typeof responseBody.data.has_more
    ).toBe('boolean');
  }
);

// =====================================================
// VOLUNTEER OPPORTUNITY GET LIST - LOGGED-IN
// =====================================================

test(
  'Volunteer Opportunity List API - Logged-in user can view opportunities',
  async ({ request }) => {
    expect(USER_SID).toBeTruthy();

    const response = await request.get(
      `${BASE_URL}/api/method/citizen_connect_app.api.volunteer_opportunity.get_list`,
      {
        headers: {
          Cookie: `sid=${USER_SID}`,
        },
      }
    );

    const responseBody = await response.json();

    console.log(
      'Logged-in Volunteer Opportunity List Status:',
      response.status()
    );

    console.log(
      'Logged-in Volunteer Opportunity List Response:',
      responseBody
    );

    expect(response.status()).toBe(200);
    expect(responseBody.status).toBe('success');

    expect(responseBody.data).toBeTruthy();

    expect(
      Array.isArray(responseBody.data.opportunities)
    ).toBe(true);

    expect(responseBody.data.limit).toBe(10);
    expect(responseBody.data.offset).toBe(0);

    expect(
      typeof responseBody.data.has_more
    ).toBe('boolean');
  }
);
// =====================================================
// VOLUNTEER OPPORTUNITY GET - GUEST
// =====================================================

test(
  'Volunteer Opportunity API - Guest user can view opportunity',
  async ({ request }) => {
    const opportunityId = '9hgiq2b79e';

    const response = await request.get(
      `${BASE_URL}/api/method/citizen_connect_app.api.volunteer_opportunity.get?opportunity_id=${opportunityId}`
    );

    const responseBody = await response.json();

    console.log(
      'Guest Volunteer Opportunity GET Status:',
      response.status()
    );

    console.log(
      'Guest Volunteer Opportunity GET Response:',
      responseBody
    );

    // 1. Validate HTTP status
    expect(response.status()).toBe(200);

    // 2. Validate top-level response keys
    expect(responseBody).toHaveProperty('message');
    expect(responseBody).toHaveProperty('status');
    expect(responseBody).toHaveProperty('data');

    // 3. Validate opportunity data exists
    expect(responseBody.data).toBeTruthy();

    const data = responseBody.data;

    // 4. Validate opportunity keys
    expect(data).toHaveProperty('id');
    expect(data).toHaveProperty('title');
    expect(data).toHaveProperty('description');
    expect(data).toHaveProperty('skills');
    expect(data).toHaveProperty('category');
    expect(data).toHaveProperty('crisis_link');
    expect(data).toHaveProperty('language');
    expect(data).toHaveProperty('location');
    expect(data).toHaveProperty('volunteer_format');
    expect(data).toHaveProperty('expected_time');
    expect(data).toHaveProperty('start_date');
    expect(data).toHaveProperty('end_date');
    expect(data).toHaveProperty('compensation_type');
    expect(data).toHaveProperty('ngo');
    expect(data).toHaveProperty('rating');
    expect(data).toHaveProperty('status');

    // 5. Validate category keys
    expect(data.category).toHaveProperty('l1');
    expect(data.category).toHaveProperty('l2');

    expect(data.category.l1).toHaveProperty('name');
    expect(data.category.l1).toHaveProperty('display_name');

    expect(data.category.l2).toHaveProperty('name');
    expect(data.category.l2).toHaveProperty('display_name');

    // 6. Validate location keys
    expect(data.location).toHaveProperty('country');
    expect(data.location).toHaveProperty('geo1');
    expect(data.location).toHaveProperty('geo2');

    expect(data.location.country).toHaveProperty('name');
    expect(data.location.country).toHaveProperty('display_name');

    // 7. Validate NGO keys
    expect(data.ngo).toHaveProperty('id');
    expect(data.ngo).toHaveProperty('name');
    expect(data.ngo).toHaveProperty('phone');
    expect(data.ngo).toHaveProperty('email');
  }
);

// =====================================================
// VOLUNTEER OPPORTUNITY GET - LOGGED-IN
// =====================================================
test(
  'Volunteer Opportunity API - Logged-in user can view opportunity',
  async ({ request }) => {
    expect(USER_SID).toBeTruthy();

    const opportunityId = '9hgiq2b79e';

    const response = await request.get(
      `${BASE_URL}/api/method/citizen_connect_app.api.volunteer_opportunity.get?opportunity_id=${opportunityId}`,
      {
        headers: {
          Cookie: `sid=${USER_SID}`,
        },
      }
    );

    const responseBody = await response.json();

    console.log(
      'Logged-in Volunteer Opportunity GET Status:',
      response.status()
    );

    console.log(
      'Logged-in Volunteer Opportunity GET Response:',
      responseBody
    );

    // 1. Validate HTTP status
    expect(response.status()).toBe(200);

    // 2. Validate top-level response keys
    expect(responseBody).toHaveProperty('message');
    expect(responseBody).toHaveProperty('status');
    expect(responseBody).toHaveProperty('data');

    // 3. Validate opportunity data exists
    expect(responseBody.data).toBeTruthy();

    const data = responseBody.data;

    // 4. Validate opportunity keys
    expect(data).toHaveProperty('id');
    expect(data).toHaveProperty('title');
    expect(data).toHaveProperty('description');
    expect(data).toHaveProperty('skills');
    expect(data).toHaveProperty('category');
    expect(data).toHaveProperty('crisis_link');
    expect(data).toHaveProperty('language');
    expect(data).toHaveProperty('location');
    expect(data).toHaveProperty('volunteer_format');
    expect(data).toHaveProperty('expected_time');
    expect(data).toHaveProperty('start_date');
    expect(data).toHaveProperty('end_date');
    expect(data).toHaveProperty('compensation_type');
    expect(data).toHaveProperty('ngo');
    expect(data).toHaveProperty('rating');
    expect(data).toHaveProperty('status');

    // 5. Validate category keys
    expect(data.category).toHaveProperty('l1');
    expect(data.category).toHaveProperty('l2');

    expect(data.category.l1).toHaveProperty('name');
    expect(data.category.l1).toHaveProperty('display_name');

    expect(data.category.l2).toHaveProperty('name');
    expect(data.category.l2).toHaveProperty('display_name');

    // 6. Validate location keys
    expect(data.location).toHaveProperty('country');
    expect(data.location).toHaveProperty('geo1');
    expect(data.location).toHaveProperty('geo2');

    expect(data.location.country).toHaveProperty('name');
    expect(data.location.country).toHaveProperty('display_name');

    // 7. Validate NGO keys
    expect(data.ngo).toHaveProperty('id');
    expect(data.ngo).toHaveProperty('name');
    expect(data.ngo).toHaveProperty('phone');
    expect(data.ngo).toHaveProperty('email');
  }
);

// =====================================================
// CRISIS GET LIST - GUEST
// =====================================================

test(
  'Crisis List API - Guest user can view active crises',
  async ({ request }) => {
    const response = await request.get(
      `${BASE_URL}/api/method/citizen_connect_app.api.crisis.get_list?country=&category=&status=active`
    );

    const responseBody = await response.json();

    console.log(
      'Guest Crisis List Status:',
      response.status()
    );

    console.log(
      'Guest Crisis List Response:',
      responseBody
    );

    expect(response.status()).toBe(200);
    expect(responseBody.status).toBe('success');

    expect(responseBody.data).toBeTruthy();
    expect(Array.isArray(responseBody.data)).toBe(true);
  }
);


// =====================================================
// CRISIS GET LIST - LOGGED-IN
// =====================================================

test(
  'Crisis List API - Logged-in user can view active crises',
  async ({ request }) => {
    expect(USER_SID).toBeTruthy();

    const response = await request.get(
      `${BASE_URL}/api/method/citizen_connect_app.api.crisis.get_list?country=&category=&status=active`,
      {
        headers: {
          Cookie: `sid=${USER_SID}`,
        },
      }
    );

    const responseBody = await response.json();

    console.log(
      'Logged-in Crisis List Status:',
      response.status()
    );

    console.log(
      'Logged-in Crisis List Response:',
      responseBody
    );

    expect(response.status()).toBe(200);
    expect(responseBody.status).toBe('success');

    expect(responseBody.data).toBeTruthy();
    expect(Array.isArray(responseBody.data)).toBe(true);
  }
);


// =====================================================
// CRISIS GET - GUEST
// =====================================================


test(
  'Crisis API - Guest user can view crisis',
  async ({ request }) => {
    const crisisId = 'ag285kkajq';

    const response = await request.get(
      `${BASE_URL}/api/method/citizen_connect_app.api.crisis.get?crisis_id=${crisisId}`
    );

    const responseBody = await response.json();

    console.log('Guest Crisis GET Status:', response.status());
    console.log('Guest Crisis GET Response:', responseBody);

    expect(response.status()).toBe(200);

    expect(responseBody).toHaveProperty('message');
    expect(responseBody).toHaveProperty('status');
    expect(responseBody).toHaveProperty('data');

    expect(responseBody.data).toBeTruthy();

    const data = responseBody.data;

    expect(data).toHaveProperty('id');
    expect(data).toHaveProperty('title');
    expect(data).toHaveProperty('category');
    expect(data).toHaveProperty('media');
    expect(data).toHaveProperty('description');
    expect(data).toHaveProperty('location');
    expect(data).toHaveProperty('start_date');
    expect(data).toHaveProperty('impact');
    expect(data).toHaveProperty('resources_needed');
    expect(data).toHaveProperty('emergency_contacts');
    expect(data).toHaveProperty('status');
    expect(data).toHaveProperty('collaborators');
    expect(data).toHaveProperty('crisis_summary');
    expect(data).toHaveProperty('donation_opportunity');
    expect(data).toHaveProperty('volunteer_opportunity');
    expect(data).toHaveProperty('resource_dropoff_location');

    // Location keys
    expect(data.location).toHaveProperty('country');
    expect(data.location).toHaveProperty('geo1');
    expect(data.location).toHaveProperty('geo2');

    // Media item keys
    expect(Array.isArray(data.media)).toBe(true);
    if (data.media.length > 0) {
      expect(data.media[0]).toHaveProperty('media');
      expect(data.media[0]).toHaveProperty('caption');
    }

    // Resource item keys
    expect(Array.isArray(data.resources_needed)).toBe(true);
    if (data.resources_needed.length > 0) {
      expect(data.resources_needed[0]).toHaveProperty('resource_name');
      expect(data.resources_needed[0]).toHaveProperty('quantity_requirement');
      expect(data.resources_needed[0]).toHaveProperty('qunatity_recieved');
      expect(data.resources_needed[0]).toHaveProperty('unit');
      expect(data.resources_needed[0]).toHaveProperty('priority');
      expect(data.resources_needed[0]).toHaveProperty('is_active');
    }

    // Emergency contact item keys
    expect(Array.isArray(data.emergency_contacts)).toBe(true);
    if (data.emergency_contacts.length > 0) {
      expect(data.emergency_contacts[0]).toHaveProperty('agency_name');
      expect(data.emergency_contacts[0]).toHaveProperty('contact_number');
      expect(data.emergency_contacts[0]).toHaveProperty('agency_category');
    }

    // Collaborator item keys
    expect(Array.isArray(data.collaborators)).toBe(true);
    if (data.collaborators.length > 0) {
      expect(data.collaborators[0]).toHaveProperty('user');
      expect(data.collaborators[0]).toHaveProperty('is_active');
    }

    // Volunteer opportunity item keys
    expect(Array.isArray(data.volunteer_opportunity)).toBe(true);
    if (data.volunteer_opportunity.length > 0) {
      expect(data.volunteer_opportunity[0]).toHaveProperty('child_vol_opportunity');
      expect(data.volunteer_opportunity[0]).toHaveProperty('num_of_volunteer');
      expect(data.volunteer_opportunity[0]).toHaveProperty('title');
      expect(data.volunteer_opportunity[0]).toHaveProperty('start_date');
      expect(data.volunteer_opportunity[0]).toHaveProperty('end_date');
      expect(data.volunteer_opportunity[0]).toHaveProperty('volunteer_format');
    }

    // Resource drop-off location keys
    expect(data.resource_dropoff_location).toHaveProperty('person_name');
    expect(data.resource_dropoff_location).toHaveProperty('phone_num');
    expect(data.resource_dropoff_location).toHaveProperty('time');
    expect(data.resource_dropoff_location).toHaveProperty('location_name');
    expect(data.resource_dropoff_location).toHaveProperty('location_address');
  }
);

// =====================================================
// CRISIS GET - LOGGED-IN
// =====================================================
test(
  'Crisis API - Logged-in user can view crisis',
  async ({ request }) => {
    expect(USER_SID).toBeTruthy();

    const crisisId = 'ag285kkajq';

    const response = await request.get(
      `${BASE_URL}/api/method/citizen_connect_app.api.crisis.get?crisis_id=${crisisId}`,
      {
        headers: {
          Cookie: `sid=${USER_SID}`,
        },
      }
    );

    const responseBody = await response.json();

    console.log('Logged-in Crisis GET Status:', response.status());
    console.log('Logged-in Crisis GET Response:', responseBody);

    expect(response.status()).toBe(200);

    expect(responseBody).toHaveProperty('message');
    expect(responseBody).toHaveProperty('status');
    expect(responseBody).toHaveProperty('data');

    expect(responseBody.data).toBeTruthy();

    const data = responseBody.data;

    expect(data).toHaveProperty('id');
    expect(data).toHaveProperty('title');
    expect(data).toHaveProperty('category');
    expect(data).toHaveProperty('media');
    expect(data).toHaveProperty('description');
    expect(data).toHaveProperty('location');
    expect(data).toHaveProperty('start_date');
    expect(data).toHaveProperty('impact');
    expect(data).toHaveProperty('resources_needed');
    expect(data).toHaveProperty('emergency_contacts');
    expect(data).toHaveProperty('status');
    expect(data).toHaveProperty('collaborators');
    expect(data).toHaveProperty('crisis_summary');
    expect(data).toHaveProperty('donation_opportunity');
    expect(data).toHaveProperty('volunteer_opportunity');
    expect(data).toHaveProperty('resource_dropoff_location');

    // Location keys
    expect(data.location).toHaveProperty('country');
    expect(data.location).toHaveProperty('geo1');
    expect(data.location).toHaveProperty('geo2');

    // Media item keys
    expect(Array.isArray(data.media)).toBe(true);
    if (data.media.length > 0) {
      expect(data.media[0]).toHaveProperty('media');
      expect(data.media[0]).toHaveProperty('caption');
    }

    // Resource item keys
    expect(Array.isArray(data.resources_needed)).toBe(true);
    if (data.resources_needed.length > 0) {
      expect(data.resources_needed[0]).toHaveProperty('resource_name');
      expect(data.resources_needed[0]).toHaveProperty('quantity_requirement');
      expect(data.resources_needed[0]).toHaveProperty('qunatity_recieved');
      expect(data.resources_needed[0]).toHaveProperty('unit');
      expect(data.resources_needed[0]).toHaveProperty('priority');
      expect(data.resources_needed[0]).toHaveProperty('is_active');
    }

    // Emergency contact item keys
    expect(Array.isArray(data.emergency_contacts)).toBe(true);
    if (data.emergency_contacts.length > 0) {
      expect(data.emergency_contacts[0]).toHaveProperty('agency_name');
      expect(data.emergency_contacts[0]).toHaveProperty('contact_number');
      expect(data.emergency_contacts[0]).toHaveProperty('agency_category');
    }

    // Collaborator item keys
    expect(Array.isArray(data.collaborators)).toBe(true);
    if (data.collaborators.length > 0) {
      expect(data.collaborators[0]).toHaveProperty('user');
      expect(data.collaborators[0]).toHaveProperty('is_active');
    }

    // Volunteer opportunity item keys
    expect(Array.isArray(data.volunteer_opportunity)).toBe(true);
    if (data.volunteer_opportunity.length > 0) {
      expect(data.volunteer_opportunity[0]).toHaveProperty('child_vol_opportunity');
      expect(data.volunteer_opportunity[0]).toHaveProperty('num_of_volunteer');
      expect(data.volunteer_opportunity[0]).toHaveProperty('title');
      expect(data.volunteer_opportunity[0]).toHaveProperty('start_date');
      expect(data.volunteer_opportunity[0]).toHaveProperty('end_date');
      expect(data.volunteer_opportunity[0]).toHaveProperty('volunteer_format');
    }

    // Resource drop-off location keys
    expect(data.resource_dropoff_location).toHaveProperty('person_name');
    expect(data.resource_dropoff_location).toHaveProperty('phone_num');
    expect(data.resource_dropoff_location).toHaveProperty('time');
    expect(data.resource_dropoff_location).toHaveProperty('location_name');
    expect(data.resource_dropoff_location).toHaveProperty('location_address');
  }
);