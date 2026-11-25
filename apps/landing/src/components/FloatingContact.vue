<script setup>
import { computed } from 'vue'
import { pagePath, siteStore, telHref } from '../useSite'

const company = computed(() => siteStore.company)

const phoneHref = computed(() => {
  const href = telHref(company.value?.phone)
  return href !== '#' ? href : 'tel:02743651005'
})

const zaloHref = computed(() => {
  const digits = String(company.value?.phone || '').split(/[~/-]/)[0].replace(/\D/g, '')
  return digits ? `https://zalo.me/${digits}` : 'https://zalo.me/02743651005'
})

const contactHref = computed(() => pagePath('contact'))
</script>

<template>
  <div class="floating-contact" aria-label="Liên hệ nhanh">
    <!-- 1. Gọi điện (Call) -->
    <a
      :href="phoneHref"
      class="fc-btn fc-call"
      title="Gọi ngay Hotline Daliang"
      aria-label="Gọi điện thoại"
    >
      <span class="fc-ring" />
      <span class="fc-halo" />
      <span class="fc-circle">
        <svg viewBox="0 0 24 24" class="fc-icon fc-shake" fill="currentColor" aria-hidden="true">
          <path d="M6.62 10.79a15.05 15.05 0 0 0 6.59 6.59l2.2-2.2a1 1 0 0 1 1.01-.24c1.12.37 2.33.57 3.58.57a1 1 0 0 1 1 1V20a1 1 0 0 1-1 1C10.61 21 3 13.39 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1c0 1.25.2 2.46.57 3.58a1 1 0 0 1-.25 1.01l-2.2 2.2z" />
        </svg>
      </span>
    </a>

    <!-- 2. Zalo -->
    <a
      :href="zaloHref"
      target="_blank"
      rel="noopener noreferrer"
      class="fc-btn fc-zalo"
      title="Chat Zalo với Daliang"
      aria-label="Chat Zalo"
    >
      <span class="fc-ring fc-delay-1" />
      <span class="fc-halo fc-delay-1" />
      <span class="fc-circle">
        <svg viewBox="0 0 48 48" class="fc-icon-zalo fc-shake-subtle" aria-hidden="true">
          <path
            fill="#ffffff"
            d="M24 6C13.5 6 5 13.6 5 23c0 5.3 2.7 10.1 7 13.2-.3 2.1-1.3 4.3-2.6 5.8-.3.4 0 1 .5.9 3.1-.4 6.4-1.8 8.6-3.4 1.8.3 3.6.5 5.5.5 10.5 0 19-7.6 19-17S34.5 6 24 6z"
          />
          <text
            x="24"
            y="26.5"
            text-anchor="middle"
            fill="#0084ff"
            font-family="Be Vietnam Pro, Arial, sans-serif"
            font-weight="800"
            font-size="12.5"
            letter-spacing="-0.3"
          >Zalo</text>
        </svg>
      </span>
    </a>

    <!-- 3. Messenger / Chat tư vấn -->
    <router-link
      :to="contactHref"
      class="fc-btn fc-mess"
      title="Nhắn tin tư vấn & nhận báo giá"
      aria-label="Nhắn tin tư vấn"
    >
      <span class="fc-ring fc-delay-2" />
      <span class="fc-halo fc-delay-2" />
      <span class="fc-circle">
        <svg viewBox="0 0 24 24" class="fc-icon fc-shake-subtle" fill="currentColor" aria-hidden="true">
          <path d="M12 3C6.48 3 2 6.92 2 11.75c0 2.76 1.46 5.22 3.75 6.82-.18 1.32-.78 2.66-1.56 3.58-.2.24.01.6.32.55 1.93-.27 3.96-1.14 5.31-2.12.71.11 1.44.17 2.18.17 5.52 0 10-3.92 10-8.75S17.52 3 12 3zm-4 9.75a1.25 1.25 0 1 1 0-2.5 1.25 1.25 0 0 1 0 2.5zm4 0a1.25 1.25 0 1 1 0-2.5 1.25 1.25 0 0 1 0 2.5zm4 0a1.25 1.25 0 1 1 0-2.5 1.25 1.25 0 0 1 0 2.5z" />
        </svg>
      </span>
    </router-link>
  </div>
</template>

<style scoped>
.floating-contact {
  position: fixed;
  right: 26px;
  bottom: 30px;
  z-index: 999;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24px;
}

.fc-btn {
  position: relative;
  width: 52px;
  height: 52px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  text-decoration: none;
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
}

/* Vòng hào quang mờ bao quanh giống ảnh mẫu */
.fc-halo {
  position: absolute;
  inset: -14px;
  border-radius: 999px;
  background: rgba(0, 136, 255, 0.18);
  animation: fc-halo-breathe 2.2s ease-in-out infinite;
  pointer-events: none;
}

/* Sóng lan tỏa nhấp nháy */
.fc-ring {
  position: absolute;
  inset: -4px;
  border-radius: 999px;
  background: rgba(0, 136, 255, 0.32);
  animation: fc-pulse-ring 1.9s cubic-bezier(0.24, 0, 0.38, 1) infinite;
  pointer-events: none;
}

.fc-delay-1 {
  animation-delay: 0.45s;
}

.fc-delay-2 {
  animation-delay: 0.9s;
}

.fc-circle {
  position: relative;
  z-index: 2;
  width: 50px;
  height: 50px;
  border-radius: 999px;
  background: linear-gradient(180deg, #0a95ff 0%, #0077e6 100%);
  color: #ffffff;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 6px 16px rgba(0, 119, 230, 0.38);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.fc-btn:hover .fc-circle {
  transform: scale(1.08);
  box-shadow: 0 8px 22px rgba(0, 119, 230, 0.52);
}

.fc-icon {
  width: 24px;
  height: 24px;
}

.fc-icon-zalo {
  width: 34px;
  height: 34px;
}

.fc-shake {
  animation: fc-phone-wiggle 1.8s ease-in-out infinite;
  transform-origin: 50% 50%;
}

.fc-shake-subtle {
  animation: fc-bob 2.2s ease-in-out infinite;
}

@keyframes fc-pulse-ring {
  0% {
    transform: scale(0.85);
    opacity: 0.85;
  }
  70% {
    transform: scale(1.55);
    opacity: 0;
  }
  100% {
    transform: scale(1.55);
    opacity: 0;
  }
}

@keyframes fc-halo-breathe {
  0%, 100% {
    transform: scale(0.96);
    opacity: 0.75;
  }
  50% {
    transform: scale(1.08);
    opacity: 1;
  }
}

@keyframes fc-phone-wiggle {
  0%, 60%, 100% {
    transform: rotate(0deg) scale(1);
  }
  10% {
    transform: rotate(-16deg) scale(1.06);
  }
  20% {
    transform: rotate(16deg) scale(1.06);
  }
  30% {
    transform: rotate(-14deg) scale(1.06);
  }
  40% {
    transform: rotate(14deg) scale(1.06);
  }
  50% {
    transform: rotate(-6deg) scale(1.02);
  }
}

@keyframes fc-bob {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.06);
  }
}

@media (max-width: 640px) {
  .floating-contact {
    right: 18px;
    bottom: 22px;
    gap: 20px;
  }
  .fc-btn {
    width: 46px;
    height: 46px;
  }
  .fc-circle {
    width: 44px;
    height: 44px;
  }
  .fc-halo {
    inset: -11px;
  }
  .fc-icon {
    width: 21px;
    height: 21px;
  }
  .fc-icon-zalo {
    width: 30px;
    height: 30px;
  }
}
</style>
