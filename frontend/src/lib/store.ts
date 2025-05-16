import { writable } from 'svelte/store';




// APPROVAL_REQUIRED TOOL Modal
type ApprovalModalState = {
  name: string;
  parameters: { [key: string]: any };
  resolver: (value: any) => void;
} | null;

export const ApprovalModalStore = writable<ApprovalModalState>(null);

export async function openApprovalModal(name: string, parameters: object) {
  return new Promise((resolve) => {
    ApprovalModalStore.set({
      name,
      parameters: { ...parameters },
      resolver: (result) => resolve(result)
    });
  });
}




//  Voice Verification Modal
type VoiceModalState = {
  wav_file: Blob | null
  resolver: (value: any) => void;
} | null;

export const VoiceModalStore = writable<VoiceModalState>(null);

export async function openVoiceModal() {
  return new Promise((resolve) => {
    VoiceModalStore.set({
      wav_file : null,
      resolver: (result) => resolve(result)
    });
  });
}


