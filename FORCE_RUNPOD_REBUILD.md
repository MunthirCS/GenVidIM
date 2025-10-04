# How to Force RunPod to Rebuild After GitHub Push

## ✅ Git Push Confirmed Successful

- **Repository:** https://github.com/MunthirCS/GenVidIM.git
- **Latest Commit:** `87d6f3a`
- **Message:** "Fix serverless dependencies: add peft, decord, sentencepiece, fix numpy<2"
- **Status:** Pushed to origin/main successfully

---

## ⚠️ Important: RunPod Does NOT Auto-Rebuild

**RunPod serverless endpoints do NOT automatically detect GitHub changes!**

You must **manually trigger** a rebuild in the RunPod console.

---

## 🔧 Method 1: Trigger via Settings Change (Recommended)

This is the easiest way to force a rebuild:

### Steps:

1. **In the RunPod console you have open:**
   - You should see "Repository Configuration" section

2. **Make a change to force rebuild:**
   - Find the **"Build Context"** field
   - Change it from `.` to `GenVidIM`
   - Or change any setting and change it back

3. **Click "Save Endpoint"**
   - Purple button at bottom right
   - This triggers a rebuild with latest code

4. **Wait for build**
   - Status will show "Building..."
   - Takes 10-15 minutes

---

## 🔧 Method 2: Use Versions/Builds Tab

If there's a separate tab for builds:

### Steps:

1. **Look for tabs at the top:**
   - "Settings"
   - "Versions" or "Builds"
   - "Logs"
   - Click on **"Versions"** or **"Builds"**

2. **Find rebuild option:**
   - Look for "Deploy New Version" button
   - Or "Rebuild Latest" button
   - Or "Create New Build" button

3. **Select the commit:**
   - Should show commit `87d6f3a`
   - Or show "main" branch
   - Select it and click deploy

4. **Confirm rebuild:**
   - Click confirm/deploy button
   - Wait 10-15 minutes

---

## 🔧 Method 3: Via API (If Console Doesn't Work)

If you can't find the rebuild button in the UI, we can use the API:

```powershell
# I can create a script for this if needed
python rebuild_via_api.py
```

Let me know if you need this option!

---

## 🔍 How to Verify It's Using Latest Code

### During Build:

Look for these in the build logs:

```
Cloning into...
Checking out files: 100%
HEAD is now at 87d6f3a Fix serverless dependencies
```

### After Build:

The verification step should show:

```
✅ All critical imports successful
```

If you see this, the new dependencies worked!

---

## 📸 What to Look For in RunPod Console

### Current Settings Screen (where you are):

```
Repository Configuration
├─ Branch: main
├─ Dockerfile Path: serverless/Dockerfile
└─ Build Context: .  ← Change this to "GenVidIM"

[Cancel]  [Save Endpoint] ← Click this after changing
```

### Alternative - Look for These Buttons:

- **"Rebuild"** button
- **"Deploy"** button  
- **"Update"** button
- **"Create New Version"** button

Any of these will trigger a rebuild!

---

## 🎯 Quick Action Checklist

- [x] Git push completed (commit 87d6f3a)
- [ ] Changed "Build Context" to `GenVidIM` in RunPod
- [ ] Clicked "Save Endpoint" button
- [ ] Verified build started (status shows "Building")
- [ ] Waited 10-15 minutes for build
- [ ] Checked build logs for success
- [ ] Tested with `python test_endpoint.py`

---

## 🚨 Troubleshooting

### "I don't see any rebuild button"

Try these locations:
1. After clicking "Save Endpoint", look for status change
2. Check tabs at top: Versions, Builds, Deployments
3. Look in the three-dot menu (⋮) on the endpoint card
4. Try refreshing the page

### "Build status says 'Ready' but not rebuilding"

The endpoint might be using cached build:
1. Make a small change to trigger rebuild:
   - Change Build Context: `.` → `GenVidIM` → Save
2. Or look for "Force Rebuild" option
3. Or manually delete and recreate the endpoint (last resort)

### "How do I know if it's rebuilding?"

Look for these indicators:
- Status changes to "Building" or "Deploying"
- Worker count drops to 0
- Build logs start showing activity
- Estimated time appears (usually 10-15 min)

---

## 📞 Need Help?

**Tell me what you see in the RunPod console:**
- What buttons are available?
- What tabs do you see at the top?
- What's the current status of the endpoint?

**Or try:**
- Take a screenshot and describe what's visible
- Let me know if you want the API rebuild script instead

---

## ✅ Expected Result

Once rebuild completes:

1. **Build logs should show:**
   ```
   Successfully installed peft-X.X.X decord-X.X.X sentencepiece-X.X.X
   ✅ All critical imports successful
   NumPy version: 1.26.4
   ```

2. **Test endpoint:**
   ```powershell
   python test_endpoint.py
   ```

3. **Should succeed without import errors!**

---

**Current Status:** Waiting for you to trigger rebuild in RunPod console

