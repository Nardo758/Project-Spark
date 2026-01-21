import { Copy, Users, Store, Car, Layers } from 'lucide-react'
import type { LayerDefinition, LayerType } from './types'

export const layerRegistry: Record<LayerType, LayerDefinition> = {
  deep_clone: {
    type: 'deep_clone',
    label: 'Deep Clone',
    description: 'Clone a successful business to your target location',
    icon: Copy,
    color: '#10b981',
    aiKeywords: ['clone', 'copy', 'replicate', 'business model', 'franchise', 'similar'],
    inputs: [
      {
        key: 'businessCategory',
        label: 'Business Category',
        type: 'combobox',
        placeholder: 'Type or select a category...',
        required: true,
        options: [
          { value: 'restaurant', label: 'Restaurant' },
          { value: 'fast_food', label: 'Fast Food' },
          { value: 'fast_casual', label: 'Fast Casual' },
          { value: 'fine_dining', label: 'Fine Dining' },
          { value: 'cafe', label: 'Cafe / Coffee Shop' },
          { value: 'bakery', label: 'Bakery' },
          { value: 'bar', label: 'Bar / Nightclub' },
          { value: 'food_truck', label: 'Food Truck' },
          { value: 'retail', label: 'Retail Store' },
          { value: 'clothing', label: 'Clothing / Apparel' },
          { value: 'grocery', label: 'Grocery Store' },
          { value: 'convenience', label: 'Convenience Store' },
          { value: 'pharmacy', label: 'Pharmacy' },
          { value: 'fitness', label: 'Fitness / Gym' },
          { value: 'yoga', label: 'Yoga / Pilates Studio' },
          { value: 'spa', label: 'Spa / Wellness' },
          { value: 'salon', label: 'Hair Salon / Barbershop' },
          { value: 'nail_salon', label: 'Nail Salon' },
          { value: 'healthcare', label: 'Healthcare / Medical' },
          { value: 'dental', label: 'Dental Office' },
          { value: 'veterinary', label: 'Veterinary / Pet' },
          { value: 'auto', label: 'Auto Service / Repair' },
          { value: 'car_wash', label: 'Car Wash' },
          { value: 'laundry', label: 'Laundry / Dry Cleaning' },
          { value: 'childcare', label: 'Childcare / Daycare' },
          { value: 'tutoring', label: 'Tutoring / Education' },
          { value: 'coworking', label: 'Coworking Space' },
          { value: 'hotel', label: 'Hotel / Lodging' },
          { value: 'other', label: 'Other' }
        ]
      },
      {
        key: 'sourceBusiness',
        label: 'Source Business to Clone',
        type: 'text',
        placeholder: 'e.g., Crumbl Cookies, Planet Fitness...'
      },
      {
        key: 'sourceLocation',
        label: 'Source Location (where it\'s successful)',
        type: 'address',
        placeholder: 'e.g., Salt Lake City, UT'
      },
      {
        key: 'includeCompetitors',
        label: 'Show Competitors in Target Area',
        type: 'toggle',
        defaultValue: true
      },
      {
        key: 'includeDemographics',
        label: 'Compare Demographics',
        type: 'toggle',
        defaultValue: true
      }
    ],
    defaultConfig: {
      sourceBusiness: '',
      sourceLocation: '',
      sourceLocationCoordinates: null,
      businessCategory: '',
      includeCompetitors: true,
      includeDemographics: true,
      analysisResult: null
    }
  },

  demographics: {
    type: 'demographics',
    label: 'Demographics',
    description: 'Population, income, and age distribution data',
    icon: Users,
    color: '#3b82f6',
    aiKeywords: ['demographics', 'population', 'income', 'age', 'census', 'people'],
    inputs: [
      {
        key: 'showPopulation',
        label: 'Population Density',
        type: 'toggle',
        defaultValue: true
      },
      {
        key: 'showIncome',
        label: 'Median Income',
        type: 'toggle',
        defaultValue: true
      },
      {
        key: 'showAge',
        label: 'Age Distribution',
        type: 'toggle',
        defaultValue: false
      },
      {
        key: 'displayMode',
        label: 'Display Mode',
        type: 'select',
        options: [
          { value: 'heatmap', label: 'Heatmap' },
          { value: 'markers', label: 'Data Points' },
          { value: 'choropleth', label: 'Choropleth' }
        ],
        defaultValue: 'heatmap'
      }
    ],
    defaultConfig: {
      showPopulation: true,
      showIncome: true,
      showAge: false,
      displayMode: 'heatmap'
    }
  },

  competition: {
    type: 'competition',
    label: 'Competition',
    description: 'Find competitors and similar businesses nearby',
    icon: Store,
    color: '#f97316',
    aiKeywords: ['competition', 'competitors', 'nearby', 'similar', 'businesses', 'stores'],
    inputs: [
      {
        key: 'searchQuery',
        label: 'Business Type',
        type: 'text',
        placeholder: 'e.g., coffee shops, gyms, restaurants...',
        required: true
      },
      {
        key: 'showRatings',
        label: 'Show Ratings',
        type: 'toggle',
        defaultValue: true
      },
      {
        key: 'showReviews',
        label: 'Show Review Count',
        type: 'toggle',
        defaultValue: true
      },
      {
        key: 'minRating',
        label: 'Minimum Rating',
        type: 'select',
        options: [
          { value: '0', label: 'Any' },
          { value: '3', label: '3+ Stars' },
          { value: '4', label: '4+ Stars' },
          { value: '4.5', label: '4.5+ Stars' }
        ],
        defaultValue: '0'
      }
    ],
    defaultConfig: {
      searchQuery: '',
      showRatings: true,
      showReviews: true,
      minRating: '0'
    }
  },

  traffic: {
    type: 'traffic',
    label: 'Traffic',
    description: 'Foot traffic and transportation patterns',
    icon: Car,
    color: '#f59e0b',
    aiKeywords: ['traffic', 'footfall', 'transportation', 'busy', 'transit'],
    inputs: [
      {
        key: 'showFootTraffic',
        label: 'Foot Traffic',
        type: 'toggle',
        defaultValue: true
      },
      {
        key: 'showTransit',
        label: 'Public Transit',
        type: 'toggle',
        defaultValue: false
      },
      {
        key: 'timeOfDay',
        label: 'Time of Day',
        type: 'select',
        options: [
          { value: 'all', label: 'All Day' },
          { value: 'morning', label: 'Morning (6am-12pm)' },
          { value: 'afternoon', label: 'Afternoon (12pm-6pm)' },
          { value: 'evening', label: 'Evening (6pm-12am)' }
        ],
        defaultValue: 'all'
      }
    ],
    defaultConfig: {
      showFootTraffic: true,
      showTransit: false,
      timeOfDay: 'all'
    }
  },

  custom: {
    type: 'custom',
    label: 'Custom Layer',
    description: 'Create a custom data layer',
    icon: Layers,
    color: '#6b7280',
    aiKeywords: ['custom', 'create', 'new', 'layer'],
    inputs: [
      {
        key: 'name',
        label: 'Layer Name',
        type: 'text',
        placeholder: 'Enter layer name...',
        required: true
      },
      {
        key: 'dataSource',
        label: 'Data Source',
        type: 'select',
        options: [
          { value: 'manual', label: 'Manual Entry' },
          { value: 'csv', label: 'CSV Upload' },
          { value: 'api', label: 'API Endpoint' }
        ],
        defaultValue: 'manual'
      }
    ],
    defaultConfig: {
      name: '',
      dataSource: 'manual'
    }
  }
}

export const defaultLayerTabs: LayerType[] = ['deep_clone', 'demographics', 'competition', 'traffic']

export function getLayerDefinition(type: LayerType): LayerDefinition {
  return layerRegistry[type]
}

export function createLayerInstance(type: LayerType, id?: string): import('./types').LayerInstance {
  const definition = layerRegistry[type]
  return {
    id: id || `${type}_${Date.now()}`,
    type,
    config: { ...definition.defaultConfig },
    visible: true,
    loading: false,
    data: null,
    error: null
  }
}
