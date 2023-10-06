#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import random
from torchvision.transforms import GaussianBlur


# Define a custom transform for Gaussian blur
def gaussian_blur(
    x,
    p=0.5,
    kernel_size_min=3,
    kernel_size_max=20,
    sigma_min=0.1,
    sigma_max=3):
    if x.ndim == 4:
        for i in range(x.shape[0]):
            if random.random() < p:
                kernel_size = random.randrange(
                    kernel_size_min,
                    kernel_size_max + 1, 2)
                sigma = random.uniform(sigma_min, sigma_max)
                x[i] = GaussianBlur(kernel_size=kernel_size, sigma=sigma)(x[i])
    return x


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
