# How to Rotate AWS Credentials After Exposing Secrets

## 🔒 Recommended: Rotate Credentials BEFORE Allowing Push

If possible, rotate your AWS credentials first, then allow the push (old secrets become harmless).

### Step 1: Create New AWS Access Key

1. Go to AWS Console → IAM → Users
2. Click on `render-s3-access` user
3. Go to **Security credentials** tab
4. Under **Access keys**, click **Create access key**
5. Select **Application running outside AWS**
6. Click **Next** → **Create access key**
7. **IMPORTANT:** Copy the Access Key ID and Secret Access Key immediately (you won't see the secret again!)

### Step 2: Update Render Environment Variables

1. Go to Render Dashboard → Your Backend Service → **Environment**
2. Update these variables:
   - `AWS_ACCESS_KEY_ID` = (new access key ID)
   - `AWS_SECRET_ACCESS_KEY` = (new secret access key)
3. Click **Save Changes**
4. Render will automatically redeploy

### Step 3: Verify New Credentials Work

1. Check Render logs after redeploy
2. Should see: `[Mem0] ✅ Successfully initialized with config`
3. Test by uploading a document or adding a memory

### Step 4: Delete Old Access Key

1. Go back to AWS Console → IAM → Users → `render-s3-access`
2. Go to **Security credentials** tab
3. Find the OLD access key (the one that was exposed)
4. Click the **X** (Delete) button
5. Confirm deletion

### Step 5: Now Allow GitHub Push (Safe!)

After rotating credentials:
- The old secrets in GitHub history become useless
- You can safely allow the push
- No security risk since old keys are deleted

## ⚠️ If You Already Allowed the Push

If you already allowed the push before rotating:

1. **IMMEDIATELY rotate credentials** (Steps 1-4 above)
2. The old secrets in GitHub history are now public
3. Delete the old keys ASAP to prevent abuse
4. Monitor AWS CloudTrail for any unauthorized access
5. Consider enabling S3 bucket logging to detect suspicious activity

## 🔍 Monitor for Unauthorized Access

1. **AWS CloudTrail:**
   - Go to AWS Console → CloudTrail
   - Check for API calls from unknown IPs
   - Look for unusual S3 operations

2. **S3 Access Logging:**
   - Enable access logging on your S3 bucket
   - Monitor for unexpected access patterns

3. **AWS Cost Monitor:**
   - Watch for unexpected S3 costs
   - Set up billing alerts

## ✅ Best Practices Going Forward

1. **Never commit secrets to Git**
   - Use environment variables
   - Use `.env` files (add to `.gitignore`)
   - Use secret management services (AWS Secrets Manager, etc.)

2. **Use IAM Roles (Better than Access Keys)**
   - If possible, use IAM roles instead of access keys
   - Roles provide temporary credentials
   - No long-lived secrets to manage

3. **Rotate Credentials Regularly**
   - Rotate access keys every 90 days
   - Use AWS IAM credential reports to track key age

4. **Use Least Privilege**
   - Only grant minimum permissions needed
   - Your current policy is good (only S3 access)

5. **Monitor and Alert**
   - Enable CloudTrail
   - Set up billing alerts
   - Monitor access logs

