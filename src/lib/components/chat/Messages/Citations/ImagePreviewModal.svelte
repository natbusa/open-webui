<script lang="ts">
  import { onDestroy } from 'svelte';
  import XMark from '$lib/components/icons/XMark.svelte';
  import ChevronLeft from '$lib/components/icons/ChevronLeft.svelte';
  import ChevronRight from '$lib/components/icons/ChevronRight.svelte';

  export let show = false;
  export let images: Array<{ src: string; alt: string; sourceName?: string }> = [];
  export let currentIndex = 0;

  let modalElement: HTMLDivElement;

  function prev() {
    currentIndex = (currentIndex - 1 + images.length) % images.length;
  }

  function next() {
    currentIndex = (currentIndex + 1) % images.length;
  }

  function handleKeydown(e: KeyboardEvent) {
    if (!show) return;
    if (e.key === 'Escape') {
      show = false;
    } else if (e.key === 'ArrowLeft') {
      prev();
    } else if (e.key === 'ArrowRight') {
      next();
    }
  }

  $: if (show && modalElement) {
    document.body.appendChild(modalElement);
    document.body.style.overflow = 'hidden';
  } else if (!show && modalElement?.parentElement === document.body) {
    document.body.removeChild(modalElement);
    document.body.style.overflow = 'unset';
  }

  onDestroy(() => {
    if (modalElement?.parentElement === document.body) {
      document.body.removeChild(modalElement);
      document.body.style.overflow = 'unset';
    }
  });
</script>

<svelte:window on:keydown={handleKeydown} />

<div bind:this={modalElement}>
  {#if show && images.length > 0}
    <!-- svelte-ignore a11y-click-events-have-key-events -->
    <!-- svelte-ignore a11y-no-static-element-interactions -->
    <div
      class="fixed inset-0 z-[999999] flex items-center justify-center bg-white dark:bg-black"
      on:click={() => (show = false)}
    >
      <div class="relative flex items-center justify-center" on:click|stopPropagation>
        <!-- Top bar: source ref (left) + close button (right) -->
        <div class="absolute -top-10 left-0 right-0 flex items-center justify-between">
          <!-- Source reference -->
          <div class="text-sm text-gray-600 dark:text-gray-400 truncate max-w-[50vw]">
            {images[currentIndex]?.sourceName || images[currentIndex]?.alt || ''}
          </div>

          <!-- Close button -->
          <button
            class="text-gray-700 dark:text-gray-300 hover:text-black dark:hover:text-white transition"
            on:click={() => (show = false)}
          >
            <XMark className="size-8" />
          </button>
        </div>

        <!-- Left nav button -->
        {#if images.length > 1}
          <button
            class="absolute left-[-3rem] bg-black/20 dark:bg-white/20 hover:bg-black/40 dark:hover:bg-white/40 rounded-full p-2 transition"
            on:click={prev}
          >
            <ChevronLeft className="size-6 text-gray-700 dark:text-gray-300" />
          </button>
        {/if}

        <!-- Image -->
        <img
          src={images[currentIndex]?.src}
          alt={images[currentIndex]?.alt}
          class="max-w-[70vw] max-h-[80vh] object-contain"
        />

        <!-- Right nav button -->
        {#if images.length > 1}
          <button
            class="absolute right-[-3rem] bg-black/20 dark:bg-white/20 hover:bg-black/40 dark:hover:bg-white/40 rounded-full p-2 transition"
            on:click={next}
          >
            <ChevronRight className="size-6 text-gray-700 dark:text-gray-300" />
          </button>
        {/if}

        <!-- Counter -->
        {#if images.length > 1}
          <div
            class="absolute -bottom-8 left-1/2 -translate-x-1/2 text-sm text-gray-600 dark:text-gray-400"
          >
            {currentIndex + 1} / {images.length}
          </div>
        {/if}
      </div>
    </div>
  {/if}
</div>
