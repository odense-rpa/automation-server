// src/fontAwesome.js

// Import Font Awesome core
import { library } from '@fortawesome/fontawesome-svg-core'

// Import the Font Awesome Vue component
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'

// Import specific icons
import {
  faBell,
  faEnvelope,
  faCog,
  faChevronLeft,
  faChevronRight,
  faSearch,
  faCheck,
  faEllipsisV,
  faRedo,
  faTrashAlt,
  faPencilAlt,
  faCopy,
  faCircle,
  faTimes,
  faXmarkCircle,
  faTriangleExclamation
} from '@fortawesome/free-solid-svg-icons'

// Add icons to the library
library.add(
  faBell,
  faEnvelope,
  faCog,
  faChevronLeft,
  faChevronRight,
  faSearch,
  faCheck,
  faEllipsisV,
  faRedo,
  faTrashAlt,
  faPencilAlt,
  faCopy,
  faCircle,
  faTimes,
  faXmarkCircle,
  faTriangleExclamation
)

// Export the FontAwesomeIcon component
export { FontAwesomeIcon }
