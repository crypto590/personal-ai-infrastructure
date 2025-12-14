import { S3Client, ListObjectsV2Command } from '@aws-sdk/client-s3';
import { config } from 'dotenv';

config();

const client = new S3Client({
  region: 'auto',
  endpoint: `https://${process.env.R2_ACCOUNT_ID}.r2.cloudflarestorage.com`,
  credentials: {
    accessKeyId: process.env.R2_ACCESS_KEY_ID!,
    secretAccessKey: process.env.R2_SECRET_ACCESS_KEY!,
  },
});

async function test() {
  console.log('Testing R2 connection...');
  console.log(`Bucket: ${process.env.R2_BUCKET}`);
  console.log(`Endpoint: https://${process.env.R2_ACCOUNT_ID}.r2.cloudflarestorage.com`);

  const list = await client.send(new ListObjectsV2Command({
    Bucket: process.env.R2_BUCKET,
    MaxKeys: 5,
  }));

  console.log('\n✅ Connection successful!');
  console.log(`Objects in bucket: ${list.KeyCount || 0}`);

  if (list.Contents && list.Contents.length > 0) {
    console.log('Recent files:');
    list.Contents.forEach(obj => console.log(`  - ${obj.Key}`));
  }
}

test().catch(err => {
  console.error('❌ Connection failed:', err.message);
  process.exit(1);
});
