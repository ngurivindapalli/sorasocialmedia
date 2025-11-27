import { useState, useEffect } from 'react'
import { Settings as SettingsIcon, Mail, Bell } from 'lucide-react'
import SocialMediaConnections from '../components/SocialMediaConnections'
import { api } from '../utils/api'
import { authUtils } from '../utils/auth'

function Settings() {
  const [user, setUser] = useState(null)
  const [emailNotifications, setEmailNotifications] = useState(true)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    loadUserSettings()
  }, [])

  const loadUserSettings = async () => {
    try {
      const userData = await authUtils.getCurrentUserFromAPI()
      if (userData) {
        setUser(userData)
        setEmailNotifications(userData.email_notifications_enabled)
      }
    } catch (err) {
      console.error('Failed to load user settings:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleToggleEmailNotifications = async () => {
    try {
      setSaving(true)
      const newValue = !emailNotifications
      await api.put('/api/user/email-notifications', null, {
        params: { enabled: newValue }
      })
      setEmailNotifications(newValue)
      if (user) {
        setUser({ ...user, email_notifications_enabled: newValue })
      }
    } catch (err) {
      console.error('Failed to update email notifications:', err)
      alert('Failed to update email notification settings')
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse">Loading settings...</div>
      </div>
    )
  }

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-semibold text-gray-900 mb-2 flex items-center gap-3">
          <SettingsIcon className="w-8 h-8" />
          Settings
        </h1>
        <p className="text-gray-600">Manage your account and preferences</p>
      </div>

      <div className="space-y-8">
        {/* Account Information */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Account Information</h2>
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Username</label>
              <p className="text-gray-900">{user?.username}</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
              <p className="text-gray-900">{user?.email}</p>
            </div>
          </div>
        </div>

        {/* Email Notifications */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Mail className="w-5 h-5 text-gray-600" />
              <div>
                <h2 className="text-xl font-semibold text-gray-900">Email Notifications</h2>
                <p className="text-sm text-gray-600 mt-1">
                  Receive email notifications when your videos are posted to social media
                </p>
              </div>
            </div>
            <button
              onClick={handleToggleEmailNotifications}
              disabled={saving}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                emailNotifications ? 'bg-blue-600' : 'bg-gray-300'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  emailNotifications ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>
        </div>

        {/* Social Media Connections */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Social Media Connections</h2>
          <SocialMediaConnections />
        </div>
      </div>
    </div>
  )
}

export default Settings

