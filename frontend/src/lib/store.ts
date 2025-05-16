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


// 송금 위험 감지
type DepositWarningModalState = {
  name: string;
  parameters: { [key: string]: any };
  exceedLimit: number;
  resolver: (value: any) => void;
} | null;

export const DepositWarningModalStore = writable<DepositWarningModalState>(null);

export async function openDepositWarningModal(name: string, parameters: object, exceedLimit: number) {
  return new Promise((resolve) => {
    DepositWarningModalStore.set({
      name,
      parameters: { ...parameters },
      exceedLimit,
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


